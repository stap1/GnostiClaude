#!/usr/bin/env python3
"""
Synastry HTML exporter — two natal wheels side by side, element-fit bars,
the inter-aspect table (from synastry.py JSON) and the reading's prose,
in the same accessible dark-gold layout as render_html.py.

Usage:
  py -3.13 render_html_synastry.py chartA.json chartB.json synastry.json \
      --reading reading.md --lang pl --out reading.html [--title "..."]
"""

import argparse
import html
import json
import sys

import re

from render_chart import L, PLANET_GLYPH, ASPECT_GLYPH, ROMAN
from render_html import (CSS, UI, UI_JS, ASPECT_NAME, esc, wheel_svg,
                         balance_bars, extract_prose, prose_html, aspect_cls,
                         tip, scrollx, topbar, tipsheet, header_sky,
                         ambient_html, transit_timeline)

UI_SYN = {
    "en": {"interaspects": "Inter-aspects (tightest first)",
           "overlays": "House overlays",
           "b_in_a": "planets in", "houses_of": "houses of",
           "fit": "Temperament fit",
           "nav_wheels": "Wheels", "nav_tozs": "Identities",
           "nav_comp": "Composite",
           "sec_tozs": "Two identities",
           "sec_comp": "Composite — the relationship chart"},
    "pl": {"interaspects": "Interaspekty (od najściślejszych)",
           "overlays": "Nakładki domów",
           "b_in_a": "planety w domach", "houses_of": "domach",
           "fit": "Dopasowanie temperamentów",
           "nav_wheels": "Koła", "nav_tozs": "Tożsamości",
           "nav_comp": "Kompozyt",
           "sec_tozs": "Dwie tożsamości",
           "sec_comp": "Kompozyt — karta relacji"},
}


ANGLE_OF = {"Conjunction": 0, "Sextile": 60, "Square": 90,
            "Trine": 120, "Opposition": 180}
TL_SPEED = {"Pluto": 0, "Neptune": 1, "Uranus": 2, "Saturn": 3, "Jupiter": 4,
            "Mars": 5, "Sun": 6, "Venus": 7, "Mercury": 8}
KEY_TARGETS = ("Sun", "Moon", "Venus", "AC", "MC")


def pair_timeline_data(tr, max_rows=24, max_slow=12, max_strings=4):
    """Adapt synastry_transits.py JSON to the natal timeline schema:
    slow orbs become window-wide bands, composite hits and string
    activations become point events with ◆ markers (multiple exact dates
    of one contact merge into a single row). Each kind gets a reserved
    share of the rows, so background bands cannot crowd out the dated
    events (and vice versa)."""
    w0, w1 = tr["meta"]["window"]
    # exact dates first: a band and its own exact hit are ONE row
    exact_of = {}
    for h in tr.get("composite_hits", []):
        exact_of.setdefault((h["body"], h["aspect"], h["target"]), []
                            ).append(h["date"])
    slow = []
    for s in tr.get("slow_orbs", []):
        key = (s["body"], s["aspect"], s["target"])
        slow.append({"body": s["body"], "natal": s["target"],
                     "aspect": s["aspect"], "angle": ANGLE_OF[s["aspect"]],
                     "start": w0, "end": w1,
                     "exact": exact_of.pop(key, []),
                     "min_orb": min(s["orb_start"], s["orb_end"])})
    slow.sort(key=lambda r: (r["min_orb"], TL_SPEED.get(r["body"], 9)))
    rows = slow[:max_slow]
    strings = {}
    for s in tr.get("string_activations", []):
        side, _, pt = s["endpoint"].partition(".")
        strings.setdefault((s["body"], s["endpoint"]), {
            "body": s["body"], "natal": pt, "side": f"{side}·",
            "aspect": "Conjunction", "angle": 0,
            "start": s["date"], "end": s["date"],
            "exact": [], "min_orb": 0.0})
        r = strings[(s["body"], s["endpoint"])]
        r["exact"].append(s["date"])
        r["start"], r["end"] = min(r["start"], s["date"]), max(r["end"], s["date"])
    rows += sorted(strings.values(),
                   key=lambda r: -len(r["exact"]))[:max_strings]
    hits = {}
    for (body, aspect, target), dates in exact_of.items():
        hits[(body, aspect, target)] = {
            "body": body, "natal": target, "aspect": aspect,
            "angle": ANGLE_OF[aspect],
            "start": min(dates), "end": max(dates),
            "exact": sorted(dates), "min_orb": 0.0}
    ordered = sorted(hits.values(), key=lambda r: (
        TL_SPEED.get(r["body"], 9),
        0 if r["natal"] in KEY_TARGETS else 1,
        1 if r["angle"] in (60,) else 0,
        r["start"]))
    rows += ordered[:max(0, max_rows - len(rows))]
    return {"meta": tr["meta"], "windows": rows,
            "lunations": tr.get("lunations", [])}


def classify(title):
    """Skeleton split: interpretive prose stays on the dial, the raw
    engine commentary goes to the Mechanism annex."""
    T = title.upper()
    if "TOŻSAMOŚCI" in T or "IDENTIT" in T:
        return "tozs"
    if "KOMPOZYT" in T or "COMPOSITE" in T:
        return "komp"
    if T.startswith("8") or "SYNTEZA" in T or "INTERPRETA" in T:
        return "read"
    return "mech"


def interaspect_table(syn, lang, limit=18):
    t = L[lang]
    rows, shown = [], 0
    for a in syn["inter_aspects"]:
        if a["angle"] not in (0, 60, 90, 120, 180) and shown >= 4:
            continue
        na = t["planets"].get(a["a"], a["a"])
        nb = t["planets"].get(a["b"], a["b"])
        nm = ASPECT_NAME[lang][a["aspect"]]
        rows.append(
            f"<tr><td>A · <span class='glyph'>{PLANET_GLYPH.get(a['a'], '')}</span> {esc(na)}</td>"
            f"<td><span class='glyph {aspect_cls(a['angle'])}'>"
            f"{ASPECT_GLYPH[a['aspect']]}</span> {esc(nm)}</td>"
            f"<td>B · <span class='glyph'>{PLANET_GLYPH.get(a['b'], '')}</span> {esc(nb)}</td>"
            f"<td class='num'>{a['orb']:.1f}°</td></tr>")
        shown += 1
        if shown >= limit:
            break
    return (f"<table><thead><tr>"
            f"<th scope='col'></th>"
            f"<th scope='col'>{tip(UI[lang]['aspect'], 'aspekt', lang)}</th>"
            f"<th scope='col'></th>"
            f"<th scope='col'>{tip(UI[lang]['orb'], 'orb', lang)}</th>"
            f"</tr></thead><tbody>{''.join(rows)}</tbody></table>")


def overlay_lists(syn, lang, nameA, nameB):
    t = L[lang]
    u = UI_SYN[lang]

    def one(direction, ov, host):
        items = "".join(
            f"<li><span class='glyph'>{PLANET_GLYPH.get(k, '')}</span> "
            f"{esc(t['planets'].get(k, k))} → {ROMAN[h - 1]}</li>"
            for k, h in ov.items())
        return (f"<div><h3>{esc(direction)} {esc(u['b_in_a'])} "
                f"{esc(host)}</h3><ul class='overlay'>{items}</ul></div>")

    return ("<div class='overlays'>"
            + one(nameB, syn["overlays_B_in_A"], nameA)
            + one(nameA, syn["overlays_A_in_B"], nameB)
            + "</div>")


EXTRA_CSS = """
.duo{display:grid;
  grid-template-columns:repeat(auto-fit,minmax(min(340px,100%),1fr));
  gap:20px;align-items:start}
.duo h3{text-align:center;color:var(--gold);font-weight:normal;margin:6px 0}
.duo h3 small.nohouses{display:block;color:var(--muted);font-size:12.5px;
  font-style:italic;margin-top:2px}
.duo svg{width:100%;height:auto}
.overlays{display:grid;
  grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));
  gap:8px 30px}
ul.overlay{list-style:none;padding:0;columns:2;font-size:14.5px}
ul.overlay li{margin:2px 0;break-inside:avoid}
@media screen and (max-width:700px){
  .duo{gap:26px}
  .overlays{gap:4px 0}
  ul.overlay{font-size:13.5px}
}
@media screen and (max-width:420px){
  ul.overlay{columns:1}
}
"""


def main():
    p = argparse.ArgumentParser(description="Synastry HTML export")
    p.add_argument("chart_a")
    p.add_argument("chart_b")
    p.add_argument("synastry_json")
    p.add_argument("--composite", help="composite.json — adds the relationship wheel")
    p.add_argument("--transits", help="transits.json (to the composite, from "
                   "synastry_transits.py) — adds the transit-timeline section")
    p.add_argument("--mark-date", help="YYYY-MM-DD to mark on the timeline")
    p.add_argument("--no-houses-b", action="store_true",
                   help="B's birth time is unknown: draw B's wheel (and the "
                        "composite) without cusps, house numbers or AC/MC")
    p.add_argument("--reading")
    p.add_argument("--lang", default="pl", choices=["en", "pl"])
    p.add_argument("--out", required=True)
    p.add_argument("--title", default=None)
    args = p.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    A = json.load(open(args.chart_a, encoding="utf-8"))
    B = json.load(open(args.chart_b, encoding="utf-8"))
    syn = json.load(open(args.synastry_json, encoding="utf-8"))
    reading = open(args.reading, encoding="utf-8").read() if args.reading else ""
    lang, u = args.lang, UI[args.lang]
    nameA, nameB = syn["meta"]["nameA"], syn["meta"]["nameB"]
    title = args.title or f"Synastria — {nameA} × {nameB}"

    us = UI_SYN[lang]
    nohb = args.no_houses_b
    nohb_note = ("<small class='nohouses'>" + {
        'pl': 'godzina urodzenia nieznana — koło bez domów i osi',
        'en': 'birth time unknown — wheel without houses or angles',
    }[lang] + "</small>") if nohb else ""
    prose, conf = extract_prose(reading) if reading else ([], [])
    groups = {"tozs": [], "komp": [], "read": [], "mech": []}
    for pt, paras in prose:
        groups[classify(pt)].append((pt, paras))

    tozs_html = "".join(prose_html(paras) for _, paras in groups["tozs"])
    komp_prose = "".join(prose_html(paras) for _, paras in groups["komp"])

    comp_wheel = ""
    if args.composite:
        comp = json.load(open(args.composite, encoding="utf-8"))
        comp_wheel = (
            f"<div class='wheelwrap' style='max-width:640px;margin:0 auto'>"
            f"{wheel_svg(comp, lang, houseless=nohb)}"
            f"{balance_bars(comp, lang)}</div>")
    composite_section = ""
    if comp_wheel or komp_prose:
        composite_section = (
            f"<section id='kompozyt'><h2>{tip(us['sec_comp'], 'kompozyt', lang)}</h2>"
            f"{comp_wheel}{komp_prose}</section>")

    tozs_section = (f"<section id='tozsamosc'><h2>{esc(us['sec_tozs'])}</h2>"
                    f"{tozs_html}</section>") if tozs_html else ""

    transits_section = ""
    if args.transits:
        tr = json.load(open(args.transits, encoding="utf-8"))
        if "windows" not in tr:  # synastry_transits.py schema
            tr = pair_timeline_data(tr)
        transits_section = (
            f"<section id='tranzyty'><h2>{esc(u['timeline'])}</h2>"
            f"{scrollx(transit_timeline(tr, lang, args.mark_date), u['timeline'])}"
            f"<p class='tl-legend'>{esc(u['tl_legend'])}</p></section>")

    reading_html = "".join(
        f"<h3>{esc(pt)}</h3>{prose_html(paras)}" for pt, paras in groups["read"])
    conf_html = ""
    if conf:
        conf_html = (f"<h2>{esc(u['confidence'])}</h2><ul class='conf'>"
                     + "".join(f"<li>{esc(c)}</li>" for c in conf) + "</ul>")

    # Mechanism annex: engine commentary around the two data blocks —
    # chart-fit prose first, then inter-aspects + method focus, overlays last.
    mech_pre, mech_focus = [], []
    for pt, paras in groups["mech"]:
        (mech_focus if re.search(r"FOKUS|FOCUS", pt.upper())
         else mech_pre).append((pt, paras))
    mech_block = lambda items: "".join(
        f"<h3 class='mech-h3'>{esc(pt)}</h3>{prose_html(paras)}"
        for pt, paras in items)
    mechanism_section = (
        f"<section id=\"mechanizm\" class=\"closed\">"
        f"<h2 aria-expanded=\"false\">{esc(u['mech_title'])}</h2>"
        f"<p class=\"mech-hint\">{esc(u['mech_hint'])}</p>"
        f"{mech_block(mech_pre)}"
        f"<h3 class='mech-h3'>{esc(us['interaspects'])}</h3>"
        f"{scrollx(interaspect_table(syn, lang), us['interaspects'])}"
        f"{mech_block(mech_focus)}"
        f"<h3 class='mech-h3'>{tip(us['overlays'], 'dom', lang)}</h3>"
        f"{overlay_lists(syn, lang, nameA, nameB)}"
        f"</section>")

    nav_links = [("#kola", us["nav_wheels"])]
    if tozs_section:
        nav_links.append(("#tozsamosc", us["nav_tozs"]))
    if composite_section:
        nav_links.append(("#kompozyt", us["nav_comp"]))
    if transits_section:
        nav_links.append(("#tranzyty", u["nav_transits"]))
    nav_links += [("#reading", u["nav_read"]), ("#mechanizm", u["nav_mech"])]

    disclaimer = {
        "pl": "Ten odczyt jest hermetycznym zwierciadłem do refleksji — mapą "
              "tendencji, nie wyrokiem o związku. Astrologia jest tradycją "
              "symboliczną i nie zastępuje profesjonalnej porady. "
              "„Jak na górze, tak na dole; poznaj samego siebie.”",
        "en": "This reading is a Hermetic mirror for reflection — a map of "
              "tendencies, not a verdict on a relationship. Astrology is a "
              "symbolic tradition, not professional advice. "
              "“As above, so below; know thyself.”",
    }[lang]

    out = f"""<!DOCTYPE html>
<html lang="{lang}">
<head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<script>try{{var _t=localStorage.getItem('astro-theme');
if(_t)document.documentElement.setAttribute('data-theme',_t);}}catch(e){{}}</script>
<style>{CSS}{EXTRA_CSS}</style></head>
<body>
<a class="skip" href="#reading">{esc(u['skip'])}</a>
{topbar(lang, links=nav_links)}
{ambient_html()}
<main>
<header class="title">
  {header_sky()}
  <div class="glyphs glyph" aria-hidden="true">☉ ☽ ☿ ♀ ♂ ♃ ♄ ♅ ♆ ♇</div>
  <h1>{esc(title)}<small>„Jak na górze, tak na dole” · Astrologia hermetyczna</small></h1>
</header>
<div class="meta">
  <span><b>A · {esc(nameA)}</b> · {esc(syn['meta']['dobA'])} · ☉ {esc(L[lang]['signs'][syn['meta']['sunA']])}</span>
  <span><b>B · {esc(nameB)}</b> · {esc(syn['meta']['dobB'])} · ☉ {esc(L[lang]['signs'][syn['meta']['sunB']])}</span>
</div>
<section class="duo" id="kola">
  <div><h3>A · {esc(nameA)}</h3>{wheel_svg(A, lang)}{balance_bars(A, lang)}</div>
  <div><h3>B · {esc(nameB)}{nohb_note}</h3>{wheel_svg(B, lang, houseless=nohb)}{balance_bars(B, lang)}</div>
</section>
{tozs_section}
{composite_section}
{transits_section}
<section class="reading" id="reading"><h2>{esc(u['reading'])}</h2>
{reading_html}{conf_html}</section>
{mechanism_section}
<footer><p>{esc(u['tiphint'])}</p><p>{esc(disclaimer)}</p><p>{esc(u['generated'])}</p></footer>
</main>
{tipsheet(lang)}
<script>{UI_JS}</script>
</body></html>"""
    open(args.out, "w", encoding="utf-8", newline="\n").write(out)
    print(f"written {args.out} ({len(out)} bytes)")


if __name__ == "__main__":
    main()
