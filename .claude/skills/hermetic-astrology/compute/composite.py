#!/usr/bin/env python3
"""
Composite (midpoint) chart — the relationship as a "third entity".

Builds a chart-shaped JSON from two natal chart.json files: every point is the
shorter-arc midpoint of the pair's same-named points (Sun–Sun, Moon–Moon, …,
Ascendant–Ascendant, MC–MC). Houses: Whole Sign from the composite Ascendant.
Aspects among composite points (phase "—": a composite has no motion).
No sect, no dignities, no lots — those belong to individuals, not midpoints.

The output is intentionally shaped like chart_engine.py output (planets/
angles/house_cusps/aspects/balance) so render_html.wheel_svg and
balance_bars work on it directly.

Usage:
  py -3.13 composite.py chartA.json chartB.json [--nameA X] [--nameB Y]
"""

import argparse
import json
import sys

from chart_engine import (SIGNS, GLYPH, ELEMENT, MODALITY, DOMICILE, ASPECTS,
                          MAJOR_ANGLES, LUMINARY_ORB_BONUS, make_point,
                          fmt_pos, norm360)

POINTS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
          "Uranus", "Neptune", "Pluto", "North Node"]


def midpoint(a, b):
    """Shorter-arc midpoint of two longitudes."""
    return norm360(a + (((b - a + 180.0) % 360.0) - 180.0) / 2.0)


def comp_aspects(points):
    names = list(points.keys())
    out = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if a in ("Ascendant", "Midheaven") and b in ("Ascendant", "Midheaven"):
                continue
            la, lb = points[a], points[b]
            diff = abs(la - lb) % 360
            if diff > 180:
                diff = 360 - diff
            lum = LUMINARY_ORB_BONUS if ("Sun" in (a, b) or "Moon" in (a, b)) else 0.0
            for aname, angle, orb in ASPECTS:
                limit = orb + (lum if angle in MAJOR_ANGLES else 0.0)
                delta = abs(diff - angle)
                if delta <= limit:
                    out.append({"a": a, "b": b, "aspect": aname, "angle": angle,
                                "orb": round(delta, 2), "phase": "—"})
                    break
    out.sort(key=lambda x: x["orb"])
    return out


def main():
    p = argparse.ArgumentParser(description="Midpoint composite of two charts")
    p.add_argument("chart_a")
    p.add_argument("chart_b")
    p.add_argument("--nameA", default=None)
    p.add_argument("--nameB", default=None)
    args = p.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    A = json.load(open(args.chart_a, encoding="utf-8"))
    B = json.load(open(args.chart_b, encoding="utf-8"))
    for c, path in ((A, args.chart_a), (B, args.chart_b)):
        if "error" in c:
            print(json.dumps({"error": f"bad chart {path}: {c['error']}"}))
            sys.exit(1)

    asc = midpoint(A["angles"]["Ascendant"]["lon"], B["angles"]["Ascendant"]["lon"])
    mc = midpoint(A["angles"]["Midheaven"]["lon"], B["angles"]["Midheaven"]["lon"])
    asc_idx = int(asc // 30)
    cusps = [((asc_idx + i) % 12) * 30.0 for i in range(12)]  # Whole Sign

    planets = {}
    for k in POINTS:
        if k in A["planets"] and k in B["planets"]:
            planets[k] = make_point(
                midpoint(A["planets"][k]["lon"], B["planets"][k]["lon"]), cusps)
    if "North Node" in planets:
        planets["South Node"] = make_point(
            norm360(planets["North Node"]["lon"] + 180.0), cusps)

    mc_idx = int(mc // 30)
    angles = {
        "Ascendant": {"lon": round(asc, 4), "sign": SIGNS[asc_idx],
                      "sign_glyph": GLYPH[SIGNS[asc_idx]],
                      "position": fmt_pos(asc), "ruler": DOMICILE[asc_idx]},
        "Midheaven": {"lon": round(mc, 4), "sign": SIGNS[mc_idx],
                      "sign_glyph": GLYPH[SIGNS[mc_idx]],
                      "position": fmt_pos(mc), "ruler": DOMICILE[mc_idx]},
    }

    el = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    mo = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}
    for k, d in planets.items():
        if k == "South Node":
            continue
        el[ELEMENT[d["sign_idx"]]] += 1
        mo[MODALITY[d["sign_idx"]]] += 1
    el[ELEMENT[asc_idx]] += 1
    mo[MODALITY[asc_idx]] += 1

    apts = {k: v["lon"] for k, v in planets.items() if k != "South Node"}
    apts["Ascendant"] = asc
    apts["Midheaven"] = mc

    out = {
        "meta": {
            "nameA": args.nameA or A["meta"]["name"],
            "nameB": args.nameB or B["meta"]["name"],
            "dobA": A["meta"]["dob"], "dobB": B["meta"]["dob"],
            "method": "composite (shorter-arc midpoints)",
            "house_system_effective": "Whole Sign (from composite ASC)",
            "zodiac": "Tropical",
        },
        "angles": angles,
        "house_cusps": cusps,
        "planets": planets,
        "aspects": comp_aspects(apts),
        "balance": {"elements": el, "modalities": mo},
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
