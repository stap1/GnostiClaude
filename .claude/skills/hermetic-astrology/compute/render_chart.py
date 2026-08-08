#!/usr/bin/env python3
"""
Chart renderer — turns chart_engine.py JSON into the beautified, 72-column
box-drawing blocks used by templates/full-reading.md (chart table, balance
bars, dignity & condition table, aspect grid, aspect list, hermetic panel).

Deterministic formatting lives here so the model never hand-aligns tables.
Interpretation (prose) is added by the skill around these blocks.

Usage:
  py -3.13 render_chart.py path/to/chart.json [--lang en|pl]
"""

import argparse
import json
import sys

W = 72  # global report width

PLANET_GLYPH = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
    "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆",
    "Pluto": "♇", "North Node": "☊", "South Node": "☋",
    "Ascendant": "AC", "Midheaven": "MC", "Fortune": "⊕", "Spirit": "⊗",
}
ASPECT_GLYPH = {
    "Conjunction": "☌", "Opposition": "☍", "Trine": "△", "Square": "□",
    "Sextile": "⚹", "Quincunx": "⚻", "Semisextile": "⚺", "Semisquare": "∠",
    "Sesquiquadrate": "⚼", "Quintile": "Q",
}
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]

GRID_ORDER = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
              "Saturn", "Uranus", "Neptune", "Pluto", "North Node"]
TRAD = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

L = {
    "en": {
        "planets": {p: p for p in PLANET_GLYPH},
        "planets_short": {"North Node": "N.Node", "South Node": "S.Node",
                          "Ascendant": "Asc.", "Midheaven": "Midheaven"},
        "signs": {s: s for s in ["Aries", "Taurus", "Gemini", "Cancer", "Leo",
                                 "Virgo", "Libra", "Scorpio", "Sagittarius",
                                 "Capricorn", "Aquarius", "Pisces"]},
        "dign": {"Domicile": "Domicile", "Exaltation": "Exaltation",
                 "Triplicity": "Triplicity", "Term": "Term", "Face": "Face",
                 "Detriment": "Detriment", "Fall": "Fall", "Peregrine": "Peregrine"},
        "sect": {"of sect": "of sect", "contrary to sect": "contrary",
                 "common": "common"},
        "solar": {"cazimi": "cazimi", "combust": "combust",
                  "under beams": "under beams", "free": "free"},
        "elements": {"Fire": "Fire", "Earth": "Earth", "Air": "Air", "Water": "Water"},
        "modes": {"Cardinal": "Cardinal", "Fixed": "Fixed", "Mutable": "Mutable"},
        "days": {"Monday": "Monday", "Tuesday": "Tuesday", "Wednesday": "Wednesday",
                 "Thursday": "Thursday", "Friday": "Friday", "Saturday": "Saturday",
                 "Sunday": "Sunday"},
        "phase": {"applying": "a", "separating": "s", "exact": "e", "—": "—"},
        "hdr": {"body": "Body", "sign": "Sign", "deg": "Degree", "hse": "Hse",
                "dign": "Dignity", "mot": "Mot", "planet": "Planet",
                "essential": "Essential dignity", "score": "Score",
                "sect": "Sect", "solar": "Solar"},
        "labels": {
            "chart": "1 · THE CHART", "dignity": "3 · DIGNITY & CONDITION",
            "aspects": "4 · ASPECTS", "hermetic": "6 · HERMETIC LAYER",
            "sig": "HERMETIC SIGNATURE",
            "sect_l": "Sect", "dayhour": "Day & hour", "decans": "Decans",
            "lots": "Lots", "solar_l": "Solar", "nodes": "Nodes",
            "ruler": "ruler", "chart_ruler": "Chart ruler", "house": "house",
            "day_of": "day of", "hour_of": "hour of", "day_chart": "Day",
            "night_chart": "Night", "growth": "growth", "release": "release",
            "all_free": "all free", "key_aspects":
                "Key aspects — tightest first · a = applying, s = separating:",
            "cusp_warn": "AC within ~1° of the sign cusp — confirm the birth time.",
        },
    },
    "pl": {
        "planets": {"Sun": "Słońce", "Moon": "Księżyc", "Mercury": "Merkury",
                    "Venus": "Wenus", "Mars": "Mars", "Jupiter": "Jowisz",
                    "Saturn": "Saturn", "Uranus": "Uran", "Neptune": "Neptun",
                    "Pluto": "Pluton", "North Node": "Węzeł Płn.",
                    "South Node": "Węzeł Płd.", "Ascendant": "Ascendent",
                    "Midheaven": "Medium Coeli", "Fortune": "Fortuna",
                    "Spirit": "Duch"},
        "planets_short": {"North Node": "Węzeł Płn.", "South Node": "Węzeł Płd.",
                          "Ascendant": "Asc.", "Midheaven": "M.Coeli"},
        "signs": {"Aries": "Baran", "Taurus": "Byk", "Gemini": "Bliźnięta",
                  "Cancer": "Rak", "Leo": "Lew", "Virgo": "Panna",
                  "Libra": "Waga", "Scorpio": "Skorpion",
                  "Sagittarius": "Strzelec", "Capricorn": "Koziorożec",
                  "Aquarius": "Wodnik", "Pisces": "Ryby"},
        "dign": {"Domicile": "Domicyl", "Exaltation": "Wywyższenie",
                 "Triplicity": "Tryplicytet", "Term": "Termy", "Face": "Oblicze",
                 "Detriment": "Wygnanie", "Fall": "Upadek", "Peregrine": "Peregryn"},
        "sect": {"of sect": "w sekcie", "contrary to sect": "przeciw",
                 "common": "neutralny"},
        "solar": {"cazimi": "cazimi", "combust": "spalenie",
                  "under beams": "pod promien.", "free": "wolny"},
        "elements": {"Fire": "Ogień", "Earth": "Ziemia", "Air": "Powietrze",
                     "Water": "Woda"},
        "modes": {"Cardinal": "Kardynalna", "Fixed": "Stała", "Mutable": "Zmienna"},
        "days": {"Monday": "poniedziałek", "Tuesday": "wtorek",
                 "Wednesday": "środa", "Thursday": "czwartek",
                 "Friday": "piątek", "Saturday": "sobota", "Sunday": "niedziela"},
        "phase": {"applying": "a", "separating": "s", "exact": "d", "—": "—"},
        "hdr": {"body": "Ciało", "sign": "Znak", "deg": "Stopień", "hse": "Dom",
                "dign": "Godność", "mot": "Ruch", "planet": "Planeta",
                "essential": "Godność esencjalna", "score": "Punkty",
                "sect": "Sekta", "solar": "Słońce"},
        "labels": {
            "chart": "1 · HOROSKOP", "dignity": "3 · GODNOŚĆ I KONDYCJA",
            "aspects": "4 · ASPEKTY", "hermetic": "6 · WARSTWA HERMETYCZNA",
            "sig": "SYGNATURA HERMETYCZNA",
            "sect_l": "Sekta", "dayhour": "Dzień i godz.", "decans": "Dekany",
            "lots": "Losy", "solar_l": "Słoneczne", "nodes": "Węzły",
            "ruler": "władca", "chart_ruler": "Władca horoskopu", "house": "dom",
            "day_of": "dzień", "hour_of": "godzina", "day_chart": "Dzienny",
            "night_chart": "Nocny", "growth": "wzrost", "release": "uwolnienie",
            "all_free": "wszystkie wolne", "key_aspects":
                "Kluczowe aspekty — od najściślejszych · a = aplikujący, "
                "s = separujący:",
            "cusp_warn": "AC ~1° od granicy znaku — warto potwierdzić godzinę.",
        },
    },
}


def pad(s, w):
    s = s or ""
    return s[:w] if len(s) > w else s + " " * (w - len(s))


def rule(title):
    body = f"─── {title} "
    return body + "─" * (W - len(body))


def deg_str(position):
    """'7°34' Libra' -> '7°34′' (prime, degree part only)."""
    return position.split(" ")[0].replace("'", "′")


def table(cols, rows, sep_after=None):
    """cols = [(width, header)], rows = list of cell-lists (pre-localized)."""
    ws = [c[0] for c in cols]
    top = "┌" + "┬".join("─" * w for w in ws) + "┐"
    hdr = "│" + "│".join(pad(" " + h, w) for (w, h) in cols) + "│"
    mid = "╞" + "╪".join("═" * w for w in ws) + "╡"
    sep = "├" + "┼".join("─" * w for w in ws) + "┤"
    bot = "└" + "┴".join("─" * w for w in ws) + "┘"
    out = [top, hdr, mid]
    for i, r in enumerate(rows):
        if sep_after is not None and i == sep_after:
            out.append(sep)
        out.append("│" + "│".join(pad(" " + c, w) for c, w in zip(r, ws)) + "│")
    out.append(bot)
    return out


def bar(n, total=12):
    n = max(0, min(n, total))
    return "█" * n + "░" * (total - n)


def render(chart, lang):
    t = L[lang]
    lines = []
    planets = chart["planets"]
    angles = chart["angles"]
    lots = chart.get("lots", {})
    herm = chart["hermetica"]
    sect = chart["meta"]["sect"]

    def pname(key, short=False):
        base = t["planets_short"].get(key) if short else None
        return base or t["planets"].get(key, key)

    def sign_cell(p):
        return f"{p['sign_glyph']} {t['signs'][p['sign']]}"

    def dign_cell(p):
        ds = p.get("dignities")
        if not ds:
            return "—"
        return "+".join(t["dign"][x] for x in ds)

    # ── 1 · chart table ──────────────────────────────────────────────
    lines.append(rule(t["labels"]["chart"]))
    cols = [(13, t["hdr"]["body"]), (16, t["hdr"]["sign"]), (8, t["hdr"]["deg"]),
            (5, t["hdr"]["hse"]), (18, t["hdr"]["dign"]), (5, t["hdr"]["mot"])]
    rows = []
    order = GRID_ORDER + ["South Node"]
    for key in order:
        if key not in planets:
            continue
        p = planets[key]
        rows.append([
            f"{PLANET_GLYPH[key]} {pname(key, short=True)}",
            sign_cell(p), deg_str(p["position"]),
            ROMAN[p["house"] - 1], dign_cell(p),
            "Rx" if p.get("retrograde") else "",
        ])
    n_planet_rows = len(rows)

    def house_of(lon):
        # the MC is not bound to house X in Whole Sign — compute from cusps
        cusps = chart["house_cusps"]
        for i in range(12):
            span = (cusps[(i + 1) % 12] - cusps[i]) % 360.0 or 360.0
            if (lon - cusps[i]) % 360.0 < span:
                return ROMAN[i]
        return "X"

    for key in ("Ascendant", "Midheaven"):
        a = angles[key]
        rows.append([
            f"{PLANET_GLYPH[key]} {pname(key, short=True)}",
            f"{a['sign_glyph']} {t['signs'][a['sign']]}",
            deg_str(a["position"]), house_of(a["lon"]),
            f"{t['labels']['ruler']}: {pname(a['ruler'])}", "",
        ])
    lines += table(cols, rows, sep_after=n_planet_rows)

    asc_deg_in = angles["Ascendant"]["lon"] % 30.0
    if asc_deg_in < 1.0 or asc_deg_in > 29.0:
        lines.append(t["labels"]["cusp_warn"])

    cr = herm["chart_ruler"]
    crp = planets.get(cr, {})
    lines.append("")
    lines.append(
        f"{t['labels']['chart_ruler']}: {pname(cr)} "
        f"({t['signs'][angles['Ascendant']['sign']]}) — "
        f"{t['signs'].get(crp.get('sign'), '?')} · "
        f"{t['labels']['house']} {ROMAN[crp['house'] - 1] if crp.get('house') else '?'} · "
        f"{dign_cell(crp)}")

    # balance bars
    lines.append("")
    el = chart["balance"]["elements"]
    mo = chart["balance"]["modalities"]
    el_glyphs = {"Fire": "♈♌♐", "Earth": "♉♍♑", "Air": "♊♎♒", "Water": "♋♏♓"}
    mo_keys = ["Cardinal", "Fixed", "Mutable"]
    el_keys = ["Fire", "Earth", "Air", "Water"]
    for i, ek in enumerate(el_keys):
        left = f"{pad(t['elements'][ek], 10)}{el_glyphs[ek]}  {bar(el[ek])}  {el[ek]}"
        if i < len(mo_keys):
            mk = mo_keys[i]
            left = pad(left, 38) + f"{pad(t['modes'][mk], 11)}{bar(mo[mk])}  {mo[mk]}"
        lines.append(left)

    # ── 3 · dignity & condition ──────────────────────────────────────
    lines.append("")
    lines.append(rule(t["labels"]["dignity"]))
    cols3 = [(12, t["hdr"]["planet"]), (23, t["hdr"]["essential"]),
             (7, t["hdr"]["score"]), (11, t["hdr"]["sect"]), (13, t["hdr"]["solar"])]
    rows3 = []
    for key in TRAD:
        p = planets[key]
        score = p.get("dignity_score", 0)
        rows3.append([
            f"{PLANET_GLYPH[key]} {pname(key)}",
            " + ".join(t["dign"][x] for x in p.get("dignities", [])) or "—",
            f"{'+' if score > 0 else '−' if score < 0 else ''}{abs(score)}",
            t["sect"].get(p.get("sect_status", ""), "—") if key != "Sun" or True else "—",
            t["solar"].get(p.get("solar_condition", ""), "—") if key != "Sun" else "—",
        ])
    lines += table(cols3, rows3)
    lines.append("cazimi ≤ 0°17′ · combust ≤ 8°30′ · sub radiis ≤ 15°")

    # ── 4 · aspect grid + list ───────────────────────────────────────
    lines.append("")
    lines.append(rule(t["labels"]["aspects"]))
    amap = {}
    for a in chart["aspects"]:
        amap[frozenset((a["a"], a["b"]))] = a
    grid = [k for k in GRID_ORDER if k in planets]
    hdr = "    " + "".join(pad(PLANET_GLYPH[k], 4) for k in grid[:-1])
    lines.append(hdr)
    for i in range(1, len(grid)):
        row = pad(" " + PLANET_GLYPH[grid[i]], 4)
        for j in range(i):
            a = amap.get(frozenset((grid[i], grid[j])))
            row += pad(ASPECT_GLYPH[a["aspect"]] if a else "·", 4)
        lines.append(row.rstrip())
    lines.append("")
    lines.append("☌ 0° · ⚺ 30° · ∠ 45° · ⚹ 60° · Q 72° · □ 90° · △ 120° · ⚻ 150° · ☍ 180°")
    lines.append("")
    lines.append(t["labels"]["key_aspects"])
    shown = 0
    for a in chart["aspects"]:
        if a["angle"] not in (0, 60, 90, 120, 150, 180) and shown >= 6:
            continue
        ga = PLANET_GLYPH.get(a["a"], a["a"][:2])
        gb = PLANET_GLYPH.get(a["b"], a["b"][:2])
        ph = t["phase"].get(a["phase"], a["phase"])
        lines.append(f" {pad(ga, 3)}{ASPECT_GLYPH[a['aspect']]}  {pad(gb, 3)}"
                     f"{pad(f'{a['orb']:.1f}°', 6)}{ph}")
        shown += 1
        if shown >= 14:
            break

    # ── 6 · hermetic panel ───────────────────────────────────────────
    lines.append("")
    lines.append(rule(t["labels"]["hermetic"]))
    box = []
    sect_word = t["labels"]["day_chart"] if sect == "day" else t["labels"]["night_chart"]
    sect_glyphs = "♃ ♄ ☉" if sect == "day" else "☽ ♀ ♂"
    box.append((t["labels"]["sect_l"], f"{sect_word} ({sect_glyphs})"))
    dow = t["days"].get(herm.get("day_of_week", ""), "")
    box.append((t["labels"]["dayhour"],
                f"{dow} · {t['labels']['day_of']} {pname(herm['planetary_day_ruler'])}"
                + (f" · {t['labels']['hour_of']} "
                   f"{pname(herm['planetary_hour_ruler'])}"
                   f" ({herm['planetary_hour_index']})"
                   if herm.get("planetary_hour_ruler") else "")))
    dec = []
    for key, gl in (("Sun", "☉"), ("Moon", "☽")):
        fr = planets[key].get("face_ruler")
        if fr:
            dec.append(f"{gl} {pname(fr)}")
    box.append((t["labels"]["decans"], " · ".join(dec)))
    if lots:
        lot_bits = []
        for lname in ("Fortune", "Spirit"):
            lo = lots.get(lname)
            if lo:  # sign glyph (not name) keeps the panel line within 72 cols
                lot_bits.append(
                    f"{PLANET_GLYPH[lname]} {pname(lname)} {deg_str(lo['position'])} "
                    f"{lo['sign_glyph']} · {ROMAN[lo['house'] - 1]}")
        box.append((t["labels"]["lots"], "  ".join(lot_bits)))
    sol = [f"{PLANET_GLYPH[k]} {t['solar'][planets[k]['solar_condition']]}"
           for k in TRAD if k != "Sun"
           and planets[k].get("solar_condition") not in (None, "free")]
    box.append((t["labels"]["solar_l"], " · ".join(sol) or t["labels"]["all_free"]))
    nn, sn = planets["North Node"], planets["South Node"]
    box.append((t["labels"]["nodes"],
                f"☊ {t['signs'][nn['sign']]} · {ROMAN[nn['house'] - 1]} — "
                f"{t['labels']['growth']}  ←→  ☋ {t['signs'][sn['sign']]} · "
                f"{ROMAN[sn['house'] - 1]} — {t['labels']['release']}"))
    title = f"┌─ {t['labels']['sig']} "
    lines.append(title + "─" * (W - len(title)))
    for k, v in box:
        lines.append(f"│ {pad(k, 12)}: {v}")
    lines.append("└" + "─" * (W - 1))

    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="Render chart.json as report blocks")
    p.add_argument("chart_json", help="path to chart.json from chart_engine.py")
    p.add_argument("--lang", default="en", choices=["en", "pl"])
    args = p.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    with open(args.chart_json, encoding="utf-8") as f:
        chart = json.load(f)
    if "error" in chart:
        print(json.dumps(chart))
        sys.exit(1)
    print(render(chart, args.lang))


if __name__ == "__main__":
    main()
