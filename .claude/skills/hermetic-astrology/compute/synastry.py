#!/usr/bin/env python3
"""
Synastry engine — compares two chart_engine.py JSON files and emits:
  * inter_aspects: aspects between A's and B's bodies (planets, nodes, AC/MC),
    same orbs as the natal engine (+2° luminary bonus on majors), sorted by orb
  * house_overlays: where each of B's planets falls in A's houses, and vice versa
  * fit: element/modality balances side by side + sign relation of the Suns

Phases are not computed (two static natal charts have no mutual motion).

Usage:
  py -3.13 synastry.py chartA.json chartB.json [--nameA "..."] [--nameB "..."]
"""

import argparse
import json
import sys

from chart_engine import ASPECTS, MAJOR_ANGLES, LUMINARY_ORB_BONUS, assign_house

BODIES = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
          "Uranus", "Neptune", "Pluto", "North Node"]
SIGN_RELATION = {0: "conjunct signs", 1: "semisextile signs", 2: "sextile signs",
                 3: "square signs", 4: "trine signs", 5: "quincunx signs",
                 6: "opposite signs"}


def points_of(chart):
    pts = {}
    for k in BODIES:
        if k in chart["planets"]:
            pts[k] = chart["planets"][k]["lon"]
    pts["Ascendant"] = chart["angles"]["Ascendant"]["lon"]
    pts["Midheaven"] = chart["angles"]["Midheaven"]["lon"]
    return pts


def inter_aspects(pa, pb):
    out = []
    for ka, la in pa.items():
        for kb, lb in pb.items():
            if ka in ("Ascendant", "Midheaven") and kb in ("Ascendant", "Midheaven"):
                continue
            diff = abs(la - lb) % 360
            if diff > 180:
                diff = 360 - diff
            lum = (LUMINARY_ORB_BONUS
                   if ("Sun" in (ka, kb) or "Moon" in (ka, kb)) else 0.0)
            for aname, angle, orb in ASPECTS:
                limit = orb + (lum if angle in MAJOR_ANGLES else 0.0)
                delta = abs(diff - angle)
                if delta <= limit:
                    out.append({"a": ka, "b": kb, "aspect": aname,
                                "angle": angle, "orb": round(delta, 2)})
                    break
    out.sort(key=lambda x: x["orb"])
    return out


def overlays(points, cusps):
    return {k: assign_house(lon, cusps) for k, lon in points.items()
            if k not in ("Ascendant", "Midheaven")}


def main():
    p = argparse.ArgumentParser(description="Synastry between two chart JSONs")
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

    pa, pb = points_of(A), points_of(B)
    sun_gap_signs = (B["planets"]["Sun"]["sign_idx"]
                     - A["planets"]["Sun"]["sign_idx"]) % 12
    sun_gap_signs = min(sun_gap_signs, 12 - sun_gap_signs)

    out = {
        "meta": {
            "nameA": args.nameA or A["meta"]["name"],
            "nameB": args.nameB or B["meta"]["name"],
            "dobA": A["meta"]["dob"], "dobB": B["meta"]["dob"],
            "sunA": A["planets"]["Sun"]["sign"],
            "sunB": B["planets"]["Sun"]["sign"],
            "suns_by_sign": SIGN_RELATION[sun_gap_signs],
        },
        "inter_aspects": inter_aspects(pa, pb),
        "overlays_B_in_A": overlays(pb, A["house_cusps"]),
        "overlays_A_in_B": overlays(pa, B["house_cusps"]),
        "fit": {
            "elements_A": A["balance"]["elements"],
            "elements_B": B["balance"]["elements"],
            "modalities_A": A["balance"]["modalities"],
            "modalities_B": B["balance"]["modalities"],
        },
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
