#!/usr/bin/env python3
"""
Synastry transits — how the current sky activates a RELATIONSHIP:
  (a) transits to the composite (midpoint) chart — the couple's own weather,
  (b) "string activations": a transiting body conjunct an endpoint of a tight
      synastry inter-aspect lights up the whole string between the two charts,
  (c) lunations (new/full moons) in the window, placed in composite houses.

Inputs: two natal chart.json, synastry.json, composite.json, a date window.
Output: one JSON with dated events (6-hour scan, Skyfield / de421).

Usage:
  py -3.13 synastry_transits.py chartA.json chartB.json synastry.json \
      composite.json --from 2026-08-01 --to 2026-09-30
"""

import argparse
import datetime as dt
import json
import os
import sys

from chart_engine import assign_house, norm360
from skyfield.api import Loader

TRANSITING = [("Sun", "sun"), ("Mars", "mars"), ("Jupiter", "jupiter barycenter"),
              ("Saturn", "saturn barycenter"), ("Uranus", "uranus barycenter"),
              ("Neptune", "neptune barycenter"), ("Pluto", "pluto barycenter"),
              ("Venus", "venus"), ("Mercury", "mercury")]
SLOW = {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"}
STRING_BODIES = {"Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"}
ASP = [(0, "Conjunction"), (60, "Sextile"), (90, "Square"),
       (120, "Trine"), (180, "Opposition")]


def main():
    p = argparse.ArgumentParser(description="Transits to a relationship")
    p.add_argument("chart_a")
    p.add_argument("chart_b")
    p.add_argument("synastry_json")
    p.add_argument("composite_json")
    p.add_argument("--from", dest="d1", required=True, help="YYYY-MM-DD")
    p.add_argument("--to", dest="d2", required=True, help="YYYY-MM-DD")
    p.add_argument("--string-orb", type=float, default=3.0,
                   help="max inter-aspect orb for string activations")
    args = p.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    A = json.load(open(args.chart_a, encoding="utf-8"))
    B = json.load(open(args.chart_b, encoding="utf-8"))
    syn = json.load(open(args.synastry_json, encoding="utf-8"))
    comp = json.load(open(args.composite_json, encoding="utf-8"))

    def points_of(c):
        pts = {k: v["lon"] for k, v in c["planets"].items() if k != "South Node"}
        pts["Ascendant"] = c["angles"]["Ascendant"]["lon"]
        pts["Midheaven"] = c["angles"]["Midheaven"]["lon"]
        return pts

    PA, PB, PC = points_of(A), points_of(B), points_of(comp)

    load = Loader(os.path.dirname(os.path.abspath(__file__)))
    ts = load.timescale()
    eph = load("de421.bsp")
    earth = eph["earth"]

    def lon_at(t, key):
        a = earth.at(t).observe(eph[key]).apparent()
        return float(norm360(a.ecliptic_latlon(epoch=t)[1].degrees))

    d1 = dt.datetime.strptime(args.d1, "%Y-%m-%d")
    d2 = dt.datetime.strptime(args.d2, "%Y-%m-%d")
    steps = int((d2 - d1).days * 4) + 4
    t0 = ts.utc(d1.year, d1.month, d1.day, 12)
    T = [ts.tt_jd(t0.tt + i * 0.25) for i in range(steps)]

    def datestr(i):
        return (d1 + dt.timedelta(hours=6 * i)).strftime("%Y-%m-%d")

    L = {name: [lon_at(t, key) for t in T] for name, key in TRANSITING}
    LMOON = [lon_at(t, "moon") for t in T]

    def crossings(seq, target):
        """Indices where seq crosses target longitude (signed, wrap-safe)."""
        hits, prev = [], None
        for i, v in enumerate(seq):
            s = ((v - target + 180.0) % 360.0) - 180.0
            if prev is not None and prev * s <= 0 and abs(s) < 2 and abs(prev) < 2:
                hits.append(i)
            prev = s
        return hits

    # (a) transits to composite points
    comp_hits = []
    for body, _ in TRANSITING:
        for pname, plon in PC.items():
            for ang, aname in ASP:
                targets = {plon + ang, plon - ang} if ang not in (0, 180) else {plon + ang}
                for tgt in targets:
                    for i in crossings(L[body], norm360(tgt)):
                        comp_hits.append({"date": datestr(i), "body": body,
                                          "aspect": aname, "target": pname})
    comp_hits.sort(key=lambda x: x["date"])

    # slow-planet orbs to composite points at window edges
    slow_orbs = []
    for body in SLOW:
        l1, l2 = L[body][0], L[body][-1]
        for pname, plon in PC.items():
            for ang, aname in ASP:
                def orbof(l):
                    d = abs(l - plon) % 360
                    if d > 180:
                        d = 360 - d
                    return abs(d - ang)
                o1, o2 = orbof(l1), orbof(l2)
                if min(o1, o2) < 3.0:
                    slow_orbs.append({"body": body, "aspect": aname,
                                      "target": pname,
                                      "orb_start": round(o1, 1),
                                      "orb_end": round(o2, 1)})

    # (b) string activations: transit conjunct an endpoint of a tight inter-aspect
    strings = []
    tight = [x for x in syn["inter_aspects"]
             if x["angle"] in (0, 60, 90, 120, 180) and x["orb"] <= args.string_orb
             and x["a"] in PA and x["b"] in PB]
    for body in STRING_BODIES:
        for x in tight:
            for side, pts, pt in (("A", PA, x["a"]), ("B", PB, x["b"])):
                for i in crossings(L[body], pts[pt]):
                    strings.append({
                        "date": datestr(i), "body": body,
                        "endpoint": f"{side}.{pt}",
                        "string": f"A.{x['a']} {x['aspect']} B.{x['b']} "
                                  f"({x['orb']}°)"})
    strings.sort(key=lambda x: x["date"])

    # (c) lunations with composite houses
    lunations = []
    prev = None
    for i in range(len(T)):
        e = (LMOON[i] - L["Sun"][i]) % 360
        if prev is not None:
            if prev > 350 and e < 10:
                m = LMOON[i]
                lunations.append({"date": datestr(i), "type": "new_moon",
                                  "lon": round(m, 1),
                                  "composite_house": assign_house(m, comp["house_cusps"])})
            if prev < 180 <= e:
                m = LMOON[i]
                lunations.append({"date": datestr(i), "type": "full_moon",
                                  "lon": round(m, 1),
                                  "composite_house": assign_house(m, comp["house_cusps"])})
        prev = e

    print(json.dumps({
        "meta": {"window": [args.d1, args.d2],
                 "nameA": syn["meta"]["nameA"], "nameB": syn["meta"]["nameB"]},
        "composite_hits": comp_hits,
        "slow_orbs": slow_orbs,
        "string_activations": strings,
        "lunations": lunations,
    }, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
