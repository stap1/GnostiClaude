#!/usr/bin/env python3
"""
Natal transits — working windows of slow-planet transits to natal points
over a date range, plus lunations. Feeds the HTML timeline
(render_html.py --transits).

For every (transiting body × natal point × major aspect) the script scans
the window at a 6-hour step and reports each interval where the orb stays
within --orb (default 3°): start/end, the tight core (orb ≤ 1°), exact
hits, minimum orb and its date, and whether the body is retrograde then.

Usage:
  py -3.13 transits.py chart.json --from 2026-08-01 --to 2026-09-30 \
      [--orb 3.0] [--bodies slow|all]
Output: JSON on stdout.
"""

import argparse
import datetime as dt
import json
import os
import sys

from chart_engine import assign_house, norm360
from skyfield.api import Loader

BODIES = [("Sun", "sun"), ("Mercury", "mercury"), ("Venus", "venus"),
          ("Mars", "mars"), ("Jupiter", "jupiter barycenter"),
          ("Saturn", "saturn barycenter"), ("Uranus", "uranus barycenter"),
          ("Neptune", "neptune barycenter"), ("Pluto", "pluto barycenter")]
SLOW = {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"}
ASP = [(0, "Conjunction"), (60, "Sextile"), (90, "Square"),
       (120, "Trine"), (180, "Opposition")]
STEP_H = 6


def main():
    p = argparse.ArgumentParser(description="Natal transit windows")
    p.add_argument("chart_json")
    p.add_argument("--from", dest="d1", required=True, help="YYYY-MM-DD")
    p.add_argument("--to", dest="d2", required=True, help="YYYY-MM-DD")
    p.add_argument("--orb", type=float, default=3.0)
    p.add_argument("--bodies", choices=["slow", "all"], default="slow")
    args = p.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    chart = json.load(open(args.chart_json, encoding="utf-8"))
    points = {k: v["lon"] for k, v in chart["planets"].items()
              if k != "South Node"}
    points["Ascendant"] = chart["angles"]["Ascendant"]["lon"]
    points["Midheaven"] = chart["angles"]["Midheaven"]["lon"]
    for k, v in (chart.get("lots") or {}).items():
        points[k] = v["lon"]

    bodies = [(n, k) for n, k in BODIES
              if args.bodies == "all" or n in SLOW]

    load = Loader(os.path.dirname(os.path.abspath(__file__)))
    ts = load.timescale()
    eph = load("de421.bsp")
    earth = eph["earth"]

    def lon_at(t, key):
        a = earth.at(t).observe(eph[key]).apparent()
        return float(norm360(a.ecliptic_latlon(epoch=t)[1].degrees))

    d1 = dt.datetime.strptime(args.d1, "%Y-%m-%d")
    d2 = dt.datetime.strptime(args.d2, "%Y-%m-%d")
    steps = int((d2 - d1).days * 24 / STEP_H) + 1
    t0 = ts.utc(d1.year, d1.month, d1.day, 12)
    T = [ts.tt_jd(t0.tt + i * STEP_H / 24.0) for i in range(steps)]

    def datestr(i):
        return (d1 + dt.timedelta(hours=STEP_H * i)).strftime("%Y-%m-%d")

    LON = {name: [lon_at(t, key) for t in T] for name, key in bodies}
    lsun = ([lon_at(t, "sun") for t in T] if "Sun" not in LON else LON["Sun"])
    lmoon = [lon_at(t, "moon") for t in T]

    def signed(a):
        return ((a + 180.0) % 360.0) - 180.0

    windows = []
    for body, _ in bodies:
        lons = LON[body]
        for pname, plon in points.items():
            for ang, aname in ASP:
                orbs = []
                for lo in lons:
                    d = abs(lo - plon) % 360.0
                    if d > 180.0:
                        d = 360.0 - d
                    orbs.append(abs(d - ang))
                i = 0
                while i < len(orbs):
                    if orbs[i] > args.orb:
                        i += 1
                        continue
                    j = i
                    while j + 1 < len(orbs) and orbs[j + 1] <= args.orb:
                        j += 1
                    if j - i >= 1:  # ignore sub-12h blips
                        seg = orbs[i:j + 1]
                        mi = i + seg.index(min(seg))
                        tight = [k for k in range(i, j + 1) if orbs[k] <= 1.0]
                        # exact hits: sign change of the offset to either target
                        exact = []
                        tgts = {ang, -ang} if ang not in (0, 180) else {ang}
                        for tgt in tgts:
                            prev = None
                            for k in range(i, j + 1):
                                s = signed(lons[k] - plon - tgt)
                                if prev is not None and prev * s <= 0 \
                                        and abs(s) < 1 and abs(prev) < 1:
                                    exact.append(datestr(k))
                                prev = s
                        step = signed(lons[min(mi + 1, len(lons) - 1)]
                                      - lons[mi])
                        windows.append({
                            "body": body, "natal": pname, "aspect": aname,
                            "angle": ang,
                            "start": datestr(i), "end": datestr(j),
                            "orb_start": round(orbs[i], 2),
                            "orb_end": round(orbs[j], 2),
                            "min_orb": round(orbs[mi], 2),
                            "min_date": datestr(mi),
                            "tight_start": datestr(tight[0]) if tight else None,
                            "tight_end": datestr(tight[-1]) if tight else None,
                            "exact": sorted(set(exact)),
                            "retro": step < 0,
                        })
                    i = j + 1

    lunations = []
    prev = None
    for i in range(len(T)):
        e = (lmoon[i] - lsun[i]) % 360.0
        if prev is not None:
            if prev > 350.0 and e < 10.0:
                lunations.append({"date": datestr(i), "type": "new_moon",
                                  "lon": round(lmoon[i], 1),
                                  "natal_house": assign_house(
                                      lmoon[i], chart["house_cusps"])})
            if prev < 180.0 <= e:
                lunations.append({"date": datestr(i), "type": "full_moon",
                                  "lon": round(lmoon[i], 1),
                                  "natal_house": assign_house(
                                      lmoon[i], chart["house_cusps"])})
        prev = e

    print(json.dumps({
        "meta": {"name": chart["meta"].get("name", ""),
                 "window": [args.d1, args.d2], "orb": args.orb},
        "windows": windows,
        "lunations": lunations,
    }, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
