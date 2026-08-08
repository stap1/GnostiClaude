#!/usr/bin/env python3
"""
Hermetic / Western-Tropical Chart Engine (Skyfield edition)
===========================================================

Computes a geocentric, tropical natal chart with the traditional (Hermetic)
apparatus: essential dignities (with sect), Ptolemaic aspects (applying/
separating, luminary orb bonus, aspects to the angles), Egyptian terms &
Chaldean faces, solar condition (cazimi / combust / under beams), the
Hermetic lots (Fortune & Spirit), chart sect from the Sun's true altitude,
elemental & modal balance, and the planetary day/hour of birth (Chaldean
order, sunrise-to-sunrise days).

Astronomy backend: **Skyfield** (pure-Python, installs from wheels — no C++
compiler needed) with the JPL **de421** ephemeris (covers 1900–2049),
downloaded once and cached next to this file. Positions are GEOCENTRIC
apparent longitudes on the ecliptic of date = TROPICAL (correct for Western
astrology). Angles use apparent sidereal time (GAST) and true obliquity.

House systems: W=Whole Sign (default), E=Equal, O=Porphyry, P=Placidus
(falls back to Porphyry when circumpolar; the effective system is reported
in meta.house_system_effective).

Output: a single JSON object on stdout. On ANY failure (bad arguments, bad
date, missing dependency) it prints {"error": ...} and exits 1 so the skill
can fall back to Prompt Mode.

Usage:
  py -3.13 chart_engine.py --name "Jane" --dob 1993-06-14 --tob 15:40 \
      --lat 54.35 --lon 18.65 --tz 2 --house-system W
"""

import argparse
import datetime as dt
import json
import math
import os
import sys

try:
    from skyfield.api import Loader, wgs84
    from skyfield import almanac
    HAS_SKYFIELD = True
except ImportError:
    HAS_SKYFIELD = False

# ─────────────────────────────────────────────────────────────────────────────
# Static astrological data
# ─────────────────────────────────────────────────────────────────────────────

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

GLYPH = {"Aries": "♈", "Taurus": "♉", "Gemini": "♊", "Cancer": "♋",
         "Leo": "♌", "Virgo": "♍", "Libra": "♎", "Scorpio": "♏",
         "Sagittarius": "♐", "Capricorn": "♑", "Aquarius": "♒", "Pisces": "♓"}

ELEMENT = {0: "Fire", 1: "Earth", 2: "Air", 3: "Water",
           4: "Fire", 5: "Earth", 6: "Air", 7: "Water",
           8: "Fire", 9: "Earth", 10: "Air", 11: "Water"}

MODALITY = {0: "Cardinal", 1: "Fixed", 2: "Mutable", 3: "Cardinal",
            4: "Fixed", 5: "Mutable", 6: "Cardinal", 7: "Fixed",
            8: "Mutable", 9: "Cardinal", 10: "Fixed", 11: "Mutable"}

DOMICILE = {0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun",
            5: "Mercury", 6: "Venus", 7: "Mars", 8: "Jupiter",
            9: "Saturn", 10: "Saturn", 11: "Jupiter"}

# planet -> (exaltation sign index, traditional peak degree — informational)
EXALTATION = {"Sun": (0, 19), "Moon": (1, 3), "Mercury": (5, 15),
              "Venus": (11, 27), "Mars": (9, 28), "Jupiter": (3, 15),
              "Saturn": (6, 21)}

TERMS = {
    0:  [("Jupiter", 6), ("Venus", 12), ("Mercury", 20), ("Mars", 25), ("Saturn", 30)],
    1:  [("Venus", 8), ("Mercury", 14), ("Jupiter", 22), ("Saturn", 27), ("Mars", 30)],
    2:  [("Mercury", 6), ("Jupiter", 12), ("Venus", 17), ("Mars", 24), ("Saturn", 30)],
    3:  [("Mars", 7), ("Venus", 13), ("Mercury", 19), ("Jupiter", 26), ("Saturn", 30)],
    4:  [("Jupiter", 6), ("Venus", 11), ("Saturn", 18), ("Mercury", 24), ("Mars", 30)],
    5:  [("Mercury", 7), ("Venus", 17), ("Jupiter", 21), ("Mars", 28), ("Saturn", 30)],
    6:  [("Saturn", 6), ("Mercury", 14), ("Jupiter", 21), ("Venus", 28), ("Mars", 30)],
    7:  [("Mars", 7), ("Venus", 11), ("Mercury", 19), ("Jupiter", 24), ("Saturn", 30)],
    8:  [("Jupiter", 12), ("Venus", 17), ("Mercury", 21), ("Saturn", 26), ("Mars", 30)],
    9:  [("Mercury", 7), ("Jupiter", 14), ("Venus", 22), ("Saturn", 26), ("Mars", 30)],
    10: [("Mercury", 7), ("Venus", 13), ("Jupiter", 20), ("Mars", 25), ("Saturn", 30)],
    11: [("Venus", 12), ("Jupiter", 16), ("Mercury", 19), ("Mars", 28), ("Saturn", 30)],
}

CHALDEAN = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
FACE_CYCLE = ["Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter"]

# Triplicity rulers per William Lilly (day, night, participating).
# NOTE: Dorothean proper differs for Water: Venus day / Mars night / Moon part.
TRIPLICITY = {
    "Fire":  ("Sun", "Jupiter", "Saturn"),
    "Earth": ("Venus", "Moon", "Mars"),
    "Air":   ("Saturn", "Mercury", "Jupiter"),
    "Water": ("Mars", "Mars", "Moon"),
}

DAY_RULER = {0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
             4: "Venus", 5: "Saturn", 6: "Sun"}  # Mon=0 .. Sun=6

ASPECTS = [
    ("Conjunction", 0, 8), ("Opposition", 180, 8), ("Trine", 120, 8),
    ("Square", 90, 7), ("Sextile", 60, 6),
    ("Quincunx", 150, 3), ("Semisextile", 30, 2),
    ("Semisquare", 45, 2), ("Sesquiquadrate", 135, 2), ("Quintile", 72, 2),
]
MAJOR_ANGLES = {0, 60, 90, 120, 180}
LUMINARY_ORB_BONUS = 2.0  # extra orb on major aspects involving Sun or Moon

# Skyfield/de421 body keys (barycenters for the outer planets).
# Chiron is NOT in de421 and is intentionally omitted.
PLANET_BODIES = [
    ("Sun", "sun"), ("Moon", "moon"), ("Mercury", "mercury"),
    ("Venus", "venus"), ("Mars", "mars"),
    ("Jupiter", "jupiter barycenter"), ("Saturn", "saturn barycenter"),
    ("Uranus", "uranus barycenter"), ("Neptune", "neptune barycenter"),
    ("Pluto", "pluto barycenter"),
]

TRAD_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
DIURNAL_PLANETS = {"Sun", "Jupiter", "Saturn"}
NOCTURNAL_PLANETS = {"Moon", "Venus", "Mars"}

HOUSE_SYSTEMS = {"W": "Whole Sign", "E": "Equal", "O": "Porphyry", "P": "Placidus"}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers (backend-independent)
# ─────────────────────────────────────────────────────────────────────────────


def norm360(x):
    return x % 360.0


def sign_of(lon):
    return int(lon // 30) % 12, lon % 30.0


def pos_parts(lon):
    """(sign_idx, deg, min) from a longitude rounded to the arcminute —
    rolls over sign boundaries correctly (29°59.6' -> 0°00' next sign)."""
    total = int(round(norm360(lon) * 60.0)) % 21600
    return total // 1800, (total % 1800) // 60, total % 60


def fmt_pos(lon):
    s, d, m = pos_parts(lon)
    return f"{d}°{m:02d}' {SIGNS[s]}"


def face_ruler(lon):
    return FACE_CYCLE[(int(norm360(lon) // 10) % 36) % 7]


def term_ruler(sign_idx, deg_in_sign):
    for planet, upper in TERMS[sign_idx]:
        if deg_in_sign < upper:
            return planet
    return TERMS[sign_idx][-1][0]


def triplicity_ruler(sign_idx, sect):
    day, night, _ = TRIPLICITY[ELEMENT[sign_idx]]
    return day if sect == "day" else night


def assign_house(lon, cusps):
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        if a <= b:
            if a <= lon < b:
                return i + 1
        else:
            if lon >= a or lon < b:
                return i + 1
    return 1


def essential_dignity(planet, sign_idx, deg_in_sign, sect):
    """Five dignities + debilities, Lilly scoring. Peregrine = no essential
    dignity at all (may coexist with Detriment/Fall, and then stacks)."""
    dignities, debilities, score = [], [], 0
    if DOMICILE.get(sign_idx) == planet:
        dignities.append("Domicile"); score += 5
    ex = EXALTATION.get(planet)
    if ex and ex[0] == sign_idx:
        dignities.append("Exaltation"); score += 4
    if triplicity_ruler(sign_idx, sect) == planet:
        dignities.append("Triplicity"); score += 3
    if term_ruler(sign_idx, deg_in_sign) == planet:
        dignities.append("Term"); score += 2
    if face_ruler(sign_idx * 30 + deg_in_sign) == planet:
        dignities.append("Face"); score += 1
    if DOMICILE.get((sign_idx + 6) % 12) == planet:
        debilities.append("Detriment"); score -= 5
    if ex and (ex[0] + 6) % 12 == sign_idx:
        debilities.append("Fall"); score -= 4
    if not dignities:
        debilities.append("Peregrine"); score -= 5
    return dignities + debilities, score


def sect_status(planet, sect):
    if planet in DIURNAL_PLANETS:
        return "of sect" if sect == "day" else "contrary to sect"
    if planet in NOCTURNAL_PLANETS:
        return "of sect" if sect == "night" else "contrary to sect"
    return "common"  # Mercury


def solar_condition(elongation):
    """Classical condition relative to the Sun, from angular elongation."""
    if elongation <= 17.0 / 60.0:
        return "cazimi"
    if elongation <= 8.5:
        return "combust"
    if elongation <= 15.0:
        return "under beams"
    return "free"


def obliquity_of_date(T):
    """Mean obliquity of the ecliptic (Meeus), degrees. T = Julian centuries TT from J2000."""
    return (23.4392911 - 0.0130041667 * T - 1.63888e-7 * T * T
            + 5.03611e-7 * T ** 3)


def mean_node(T):
    """Mean longitude of the Moon's ascending node (Meeus), degrees of date."""
    return norm360(125.04452 - 1934.136261 * T + 0.0020708 * T * T + T ** 3 / 450000.0)


def mean_node_speed(T):
    """Daily motion of the mean node, deg/day (always retrograde, ~ -0.0530)."""
    return (-1934.136261 + 2 * 0.0020708 * T + 3 * T * T / 450000.0) / 36525.0


def compute_angles(ramc, lat, eps):
    """Return (asc, mc) ecliptic longitudes from RAMC, latitude, obliquity (deg)."""
    r, e, p = map(math.radians, (ramc, eps, lat))
    mc = math.degrees(math.atan2(math.sin(r), math.cos(e) * math.cos(r))) % 360
    asc = math.degrees(math.atan2(
        math.cos(r),
        -(math.sin(r) * math.cos(e) + math.tan(p) * math.sin(e)))) % 360
    return asc, mc


def placidus_cusp(ramc, lat, eps, offset_deg, frac, nocturnal):
    """Iterate one Placidus intermediate cusp; None if circumpolar.
    Diurnal cusps (11th/12th) lie EAST of the MC: RA = RAMC + SA_d * frac.
    Nocturnal cusps (2nd/3rd): RA = RAMC + 180 - SA_n * frac."""
    e, p = math.radians(eps), math.radians(lat)
    base = ramc + 180.0 if nocturnal else ramc
    lam = (base + offset_deg) % 360
    for _ in range(60):
        dec = math.asin(math.sin(e) * math.sin(math.radians(lam)))
        val = -math.tan(p) * math.tan(dec)
        if val < -1 or val > 1:
            return None  # circumpolar — Placidus undefined here
        sa = math.degrees(math.acos(val))  # semi-diurnal arc
        if nocturnal:
            alpha = (ramc + 180.0) - (180.0 - sa) * frac
        else:
            alpha = ramc + sa * frac
        ar = math.radians(alpha)
        new = math.degrees(math.atan2(math.sin(ar), math.cos(e) * math.cos(ar))) % 360
        if abs((new - lam + 180) % 360 - 180) < 1e-7:
            return new
        lam = new
    return lam


def porphyry_cusps(asc, mc):
    c = [0.0] * 12
    c[0], c[9], c[6], c[3] = asc, mc, (asc + 180) % 360, (mc + 180) % 360
    q1 = (asc - mc) % 360          # MC -> ASC quadrant (houses 11, 12)
    q2 = ((mc + 180) - asc) % 360  # ASC -> IC quadrant (houses 2, 3)
    c[10] = (mc + q1 / 3) % 360
    c[11] = (mc + 2 * q1 / 3) % 360
    c[1] = (asc + q2 / 3) % 360
    c[2] = (asc + 2 * q2 / 3) % 360
    for i, j in ((4, 10), (5, 11), (7, 1), (8, 2)):
        c[i] = (c[j] + 180) % 360
    return c


def house_cusps(asc, mc, ramc, lat, eps, system):
    """Return (cusps[12], effective_system_name). Raises ValueError on an
    unknown system letter. Placidus falls back to Porphyry when circumpolar."""
    system = (system or "W").upper()[:1]
    if system not in HOUSE_SYSTEMS:
        raise ValueError(
            f"unknown house system '{system}' — use one of "
            + ", ".join(f"{k}={v}" for k, v in HOUSE_SYSTEMS.items()))

    if system == "W":
        asc_sign = int(asc // 30)
        return [((asc_sign + i) % 12) * 30.0 for i in range(12)], "Whole Sign"
    if system == "E":
        return [(asc + i * 30.0) % 360 for i in range(12)], "Equal"
    if system == "O":
        return porphyry_cusps(asc, mc), "Porphyry"

    # Placidus
    specs = {10: (30, 1 / 3, False), 11: (60, 2 / 3, False),
             1: (60, 2 / 3, True), 2: (30, 1 / 3, True)}
    raw = {}
    for h, (off, fr, noc) in specs.items():
        v = placidus_cusp(ramc, lat, eps, off, fr, noc)
        if v is None:
            return porphyry_cusps(asc, mc), "Porphyry (Placidus circumpolar fallback)"
        raw[h] = v
    c = [0.0] * 12
    c[0], c[9], c[6], c[3] = asc, mc, (asc + 180) % 360, (mc + 180) % 360
    c[10], c[11], c[1], c[2] = raw[10], raw[11], raw[1], raw[2]
    for i, j in ((4, 10), (5, 11), (7, 1), (8, 2)):
        c[i] = (c[j] + 180) % 360
    return c, "Placidus"


def compute_aspects(points):
    """Ptolemaic + minor aspects between all point pairs (angle–angle pairs
    skipped). Luminary pairs get +2° orb on major aspects. Phase is the sign
    of d(orb)/dt; points without a 'speed' key (the angles) get phase '—'."""
    names = list(points.keys())
    out = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            pa, pb = points[a], points[b]
            if "speed" not in pa and "speed" not in pb:
                continue  # angle–angle: structurally linked, not an aspect
            la, lb = pa["lon"], pb["lon"]
            s = ((la - lb + 180.0) % 360.0) - 180.0  # signed separation
            diff = abs(s)
            lum = LUMINARY_ORB_BONUS if ("Sun" in (a, b) or "Moon" in (a, b)) else 0.0
            for aname, angle, orb in ASPECTS:
                limit = orb + (lum if angle in MAJOR_ANGLES else 0.0)
                delta = abs(diff - angle)
                if delta <= limit:
                    if "speed" not in pa or "speed" not in pb:
                        phase = "—"  # natal angles are static reference points
                    elif delta < 0.15:
                        phase = "exact"
                    else:
                        rel = pa["speed"] - pb["speed"]
                        # d(orb)/dt = sign(diff-angle) * sign(s) * rel
                        ddelta = ((1 if diff >= angle else -1)
                                  * (1 if s >= 0 else -1) * rel)
                        phase = "applying" if ddelta < 0 else "separating"
                    out.append({"a": a, "b": b, "aspect": aname, "angle": angle,
                                "orb": round(delta, 2), "phase": phase})
                    break
    out.sort(key=lambda x: x["orb"])
    return out


def chaldean_seq(day_ruler):
    start = CHALDEAN.index(day_ruler)
    return [CHALDEAN[(start + i) % 7] for i in range(24)]


# ─────────────────────────────────────────────────────────────────────────────
# Skyfield-dependent pieces
# ─────────────────────────────────────────────────────────────────────────────


def local_rise_set(ts, eph, y, m, d, lat, lon, tz):
    """Sunrise/sunset as local decimal hours for the given civil date."""
    try:
        loc = wgs84.latlon(lat, lon)
        start = ts.utc(y, m, d, -tz, 0)
        end = ts.utc(y, m, d, 24 - tz, 0)
        f = almanac.sunrise_sunset(eph, loc)
        times, events = almanac.find_discrete(start, end, f)
        sr = ss = None
        for tt, ev in zip(times, events):
            t_dt = tt.utc_datetime()
            local = (t_dt.hour + t_dt.minute / 60.0 + t_dt.second / 3600.0 + tz) % 24
            if ev == 1 and sr is None:
                sr = local
            elif ev == 0 and ss is None:
                ss = local
        if sr is not None and ss is not None:
            return sr, ss
    except Exception:
        pass
    return None


def planetary_day_hour(ts, eph, y, m, d, lat, lon, tz, birth_hour):
    """Planetary day & hour with sunrise-to-sunrise days: a birth before
    sunrise belongs to the PREVIOUS day's planetary day and hours 13–24.
    Returns (day_ruler, hour_ruler, hour_index 1..24, (sunrise, sunset))."""
    date0 = dt.date(y, m, d)
    rs = local_rise_set(ts, eph, y, m, d, lat, lon, tz)
    if not rs:
        return DAY_RULER[date0.weekday()], None, None, None  # polar day/night
    sunrise, sunset = rs

    if birth_hour < sunrise:  # night hours after the PREVIOUS day's sunset
        prev = date0 - dt.timedelta(days=1)
        rs_prev = local_rise_set(ts, eph, prev.year, prev.month, prev.day, lat, lon, tz)
        day_ruler = DAY_RULER[prev.weekday()]
        prev_sunset = rs_prev[1] if rs_prev else sunset
        night_len = (24.0 - prev_sunset + sunrise) / 12.0
        idx = min(max(int(((24.0 - prev_sunset) + birth_hour) / night_len), 0), 11)
        return day_ruler, chaldean_seq(day_ruler)[12 + idx], 13 + idx, rs

    day_ruler = DAY_RULER[date0.weekday()]
    if birth_hour < sunset:  # day hours
        length = (sunset - sunrise) / 12.0
        idx = min(max(int((birth_hour - sunrise) / length), 0), 11)
        return day_ruler, chaldean_seq(day_ruler)[idx], 1 + idx, rs

    # night hours after today's sunset (night runs to TOMORROW's sunrise)
    nxt = date0 + dt.timedelta(days=1)
    rs_next = local_rise_set(ts, eph, nxt.year, nxt.month, nxt.day, lat, lon, tz)
    next_sunrise = rs_next[0] if rs_next else sunrise
    night_len = (24.0 - sunset + next_sunrise) / 12.0
    idx = min(max(int((birth_hour - sunset) / night_len), 0), 11)
    return day_ruler, chaldean_seq(day_ruler)[12 + idx], 13 + idx, rs


def make_point(lon, cusps, speed=None, retrograde=None):
    s_idx, deg_in = sign_of(lon)
    entry = {
        "lon": round(lon, 4), "sign": SIGNS[s_idx], "sign_glyph": GLYPH[SIGNS[s_idx]],
        "sign_idx": s_idx, "deg_in_sign": round(deg_in, 2),
        "position": fmt_pos(lon), "house": assign_house(lon, cusps),
        "element": ELEMENT[s_idx], "modality": MODALITY[s_idx],
    }
    if speed is not None:
        entry["speed"] = round(float(speed), 4)
        entry["retrograde"] = bool(speed < 0) if retrograde is None else retrograde
    return entry


# ─────────────────────────────────────────────────────────────────────────────
# Main chart computation
# ─────────────────────────────────────────────────────────────────────────────


def build_chart(args):
    load = Loader(os.path.dirname(os.path.abspath(__file__)))
    ts = load.timescale()
    eph = load("de421.bsp")
    earth = eph["earth"]
    warnings = []

    born = dt.datetime.strptime(f"{args.dob} {args.tob}", "%Y-%m-%d %H:%M")
    y, m, d = born.year, born.month, born.day
    local_hour = born.hour + born.minute / 60.0
    t = ts.utc(y, m, d, 0, (local_hour - args.tz) * 60.0)
    h = 0.02  # days; central-difference step for speeds (±~29 min)
    t_minus, t_plus = ts.tt_jd(t.tt - h), ts.tt_jd(t.tt + h)

    T = float((t.tt - 2451545.0) / 36525.0)
    eps = obliquity_of_date(T)
    try:  # true obliquity (nutation in obliquity); cosmetic ~<9" refinement
        from skyfield.nutationlib import iau2000b
        _, deps = iau2000b(float(t.tt))  # units: 0.1 microarcsecond
        eps += float(deps) * 1e-7 / 3600.0
    except Exception:
        pass

    def body_lon(tt, key):
        a = earth.at(tt).observe(eph[key]).apparent()
        _, lon, _ = a.ecliptic_latlon(epoch=tt)
        return float(norm360(lon.degrees))

    # Angles from apparent sidereal time (consistent with apparent longitudes)
    ramc = float(norm360(t.gast * 15.0 + args.lon))
    asc, mc = compute_angles(ramc, args.lat, eps)
    cusps, house_system_effective = house_cusps(
        asc, mc, ramc, args.lat, eps, args.house_system)

    # Sect from the Sun's true (airless) altitude — house-system independent
    sun_lon = body_lon(t, "sun")
    observer = earth + wgs84.latlon(args.lat, args.lon)
    sun_alt = float(observer.at(t).observe(eph["sun"]).apparent().altaz()[0].degrees)
    sect = "day" if sun_alt > 0 else "night"

    planets = {}
    for label, key in PLANET_BODIES:
        try:
            lon = body_lon(t, key)
            speed = (((body_lon(t_plus, key) - body_lon(t_minus, key)
                       + 180.0) % 360.0) - 180.0) / (2 * h)
        except Exception as e:
            if label in TRAD_PLANETS:
                raise RuntimeError(f"failed to compute {label}: {e}")
            warnings.append(f"skipped {label}: {type(e).__name__}")
            continue
        entry = make_point(lon, cusps, speed=speed)
        s_idx, deg_in = entry["sign_idx"], lon % 30.0
        entry["face_ruler"] = face_ruler(lon)
        entry["term_ruler"] = term_ruler(s_idx, deg_in)
        if label != "Sun":
            elong = abs(((lon - sun_lon + 180.0) % 360.0) - 180.0)
            entry["solar_condition"] = solar_condition(elong)
            entry["elongation_deg"] = round(elong, 2)
        if label in TRAD_PLANETS:
            digs, score = essential_dignity(label, s_idx, deg_in, sect)
            entry["dignities"], entry["dignity_score"] = digs, score
            entry["sect_status"] = sect_status(label, sect)
        planets[label] = entry

    # Lunar nodes (mean node; rate ~ -0.053°/day, always retrograde)
    nn, nn_speed = mean_node(T), mean_node_speed(T)
    planets["North Node"] = make_point(nn, cusps, speed=nn_speed, retrograde=True)
    planets["South Node"] = make_point(norm360(nn + 180), cusps,
                                       speed=nn_speed, retrograde=True)

    asc_idx = int(asc // 30)
    mc_idx = int(mc // 30)
    angles = {
        "Ascendant": {"lon": round(asc, 4), "sign": SIGNS[asc_idx],
                      "sign_glyph": GLYPH[SIGNS[asc_idx]],
                      "position": fmt_pos(asc), "ruler": DOMICILE[asc_idx]},
        "Midheaven": {"lon": round(mc, 4), "sign": SIGNS[mc_idx],
                      "sign_glyph": GLYPH[SIGNS[mc_idx]],
                      "position": fmt_pos(mc), "ruler": DOMICILE[mc_idx]},
    }

    # Hermetic lots (sect-aware). Day: Fortune = ASC + Moon − Sun.
    moon_lon = planets["Moon"]["lon"]
    if sect == "day":
        fortune_lon = norm360(asc + moon_lon - sun_lon)
        spirit_lon = norm360(asc + sun_lon - moon_lon)
    else:
        fortune_lon = norm360(asc + sun_lon - moon_lon)
        spirit_lon = norm360(asc + moon_lon - sun_lon)
    lots = {}
    for lname, llon in (("Fortune", fortune_lon), ("Spirit", spirit_lon)):
        p = make_point(llon, cusps)
        p["ruler"] = DOMICILE[p["sign_idx"]]
        lots[lname] = p

    # Balance: 10 planets + North Node + Ascendant = 12 placements
    el_count = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    mo_count = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}
    for p, dat in planets.items():
        if p == "South Node":
            continue
        el_count[ELEMENT[dat["sign_idx"]]] += 1
        mo_count[MODALITY[dat["sign_idx"]]] += 1
    el_count[ELEMENT[asc_idx]] += 1
    mo_count[MODALITY[asc_idx]] += 1

    # Aspects: planets + nodes (N only) + the two angles (static points)
    aspect_points = {k: v for k, v in planets.items() if k != "South Node"}
    aspect_points["Ascendant"] = {"lon": asc}
    aspect_points["Midheaven"] = {"lon": mc}
    aspects = compute_aspects(aspect_points)

    day_ruler, hour_ruler, hour_idx, rise_set = planetary_day_hour(
        ts, eph, y, m, d, args.lat, args.lon, args.tz, local_hour)

    chart_ruler = angles["Ascendant"]["ruler"]
    cr = planets.get(chart_ruler, {})

    return {
        "meta": {
            "name": args.name, "dob": args.dob, "tob": args.tob,
            "lat": args.lat, "lon": args.lon, "tz": args.tz,
            "zodiac": "Tropical", "house_system": args.house_system,
            "house_system_effective": house_system_effective,
            "ephemeris": "Skyfield / JPL de421", "obliquity": round(eps, 4),
            "sect": sect, "warnings": warnings,
            "engine": "hermetic-astrology chart_engine (skyfield)",
        },
        "angles": angles,
        "house_cusps": [round(c, 4) for c in cusps],
        "planets": planets,
        "lots": lots,
        "aspects": aspects,
        "balance": {"elements": el_count, "modalities": mo_count},
        "hermetica": {
            "sect": sect,
            "sun_altitude_deg": round(sun_alt, 2),
            "day_of_week": ["Monday", "Tuesday", "Wednesday", "Thursday",
                            "Friday", "Saturday", "Sunday"][dt.date(y, m, d).weekday()],
            "planetary_day_ruler": day_ruler,
            "planetary_hour_ruler": hour_ruler,
            "planetary_hour_index": hour_idx,
            "sunrise_local": round(rise_set[0], 3) if rise_set else None,
            "sunset_local": round(rise_set[1], 3) if rise_set else None,
            "chart_ruler": chart_ruler,
            "chart_ruler_sign": cr.get("sign"),
            "chart_ruler_house": cr.get("house"),
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


class JsonArgumentParser(argparse.ArgumentParser):
    """Honor the error contract: JSON on stdout + exit 1, never usage text."""

    def error(self, message):
        print(json.dumps({"error": f"argument error: {message}"}))
        sys.exit(1)


def fail(msg):
    print(json.dumps({"error": msg}))
    sys.exit(1)


def main():
    p = JsonArgumentParser(description="Hermetic / Western-Tropical chart engine")
    p.add_argument("--name", default="Querent")
    p.add_argument("--dob", required=True, help="YYYY-MM-DD (1900-2049, de421 range)")
    p.add_argument("--tob", default="12:00", help="HH:MM (24h). Use 12:00 if unknown.")
    p.add_argument("--lat", type=float, required=True, help="Latitude, + = North")
    p.add_argument("--lon", type=float, required=True, help="Longitude, + = East")
    p.add_argument("--tz", type=float, required=True, help="UTC offset, e.g. 1 or -5")
    p.add_argument("--house-system", default="W",
                   help="W=Whole Sign (default), E=Equal, O=Porphyry, "
                        "P=Placidus (Porphyry fallback when circumpolar)")
    args = p.parse_args()

    try:  # zodiac glyphs on Windows consoles (cp1250 etc.)
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    if not HAS_SKYFIELD:
        print(json.dumps({
            "error": "skyfield not installed",
            "fix": "py -3.13 -m pip install skyfield",
            "fallback": "Skill should switch to Prompt Mode.",
        }))
        sys.exit(1)

    # Strict input validation (ts.utc would silently normalize overflow)
    try:
        born = dt.datetime.strptime(f"{args.dob} {args.tob}", "%Y-%m-%d %H:%M")
    except ValueError as e:
        fail(f"invalid --dob/--tob: {e}")
    if not (1900 <= born.year <= 2049):
        fail(f"date {args.dob} outside the de421 ephemeris range (1900-2049)")
    if not (-90.0 <= args.lat <= 90.0):
        fail(f"invalid --lat {args.lat} (must be -90..90)")
    if not (-180.0 <= args.lon <= 180.0):
        fail(f"invalid --lon {args.lon} (must be -180..180, + = East)")
    if not (-14.0 <= args.tz <= 14.0):
        fail(f"invalid --tz {args.tz} (must be -14..14)")

    try:
        chart = build_chart(args)
    except ValueError as e:  # e.g. unknown house system
        fail(str(e))
    except Exception as e:
        fail(f"computation failed: {e}")

    print(json.dumps(chart, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
