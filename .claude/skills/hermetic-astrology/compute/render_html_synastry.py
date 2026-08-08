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

from render_chart import L, PLANET_GLYPH, ASPECT_GLYPH, ROMAN
from render_html import (CSS, UI, ASPECT_NAME, esc, wheel_svg, balance_bars,
                         extract_prose, prose_html, aspect_cls, tip, scrollx)

UI_SYN = {
    "en": {"interaspects": "Inter-aspects (tightest first)",
           "overlays": "House overlays",
           "b_in_a": "planets in", "houses_of": "houses of",
           "fit": "Temperament fit"},
    "pl": {"interaspects": "Interaspekty (od najściślejszych)",
           "overlays": "Nakładki domów",
           "b_in_a": "planety w domach", "houses_of": "domach",
           "fit": "Dopasowanie temperamentów"},
}


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

    composite_section = ""
    if args.composite:
        comp = json.load(open(args.composite, encoding="utf-8"))
        comp_label = {"pl": "Kompozyt — karta relacji",
                      "en": "Composite — the relationship chart"}[lang]
        composite_section = (
            f"<section><h2>{tip(comp_label, 'kompozyt', lang)}</h2>"
            f"<div class='wheelwrap' style='max-width:640px;margin:0 auto'>"
            f"{wheel_svg(comp, lang)}{balance_bars(comp, lang)}</div></section>")

    prose, conf = extract_prose(reading) if reading else ([], [])
    prose_html_all = "".join(
        f"<h3>{esc(pt)}</h3>{prose_html(paras)}" for pt, paras in prose)
    conf_html = ""
    if conf:
        conf_html = (f"<h2>{esc(u['confidence'])}</h2><ul class='conf'>"
                     + "".join(f"<li>{esc(c)}</li>" for c in conf) + "</ul>")

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
<title>{esc(title)}</title><style>{CSS}{EXTRA_CSS}</style></head>
<body><main>
<header class="title">
  <div class="glyphs glyph" aria-hidden="true">☉ ☽ ☿ ♀ ♂ ♃ ♄ ♅ ♆ ♇</div>
  <h1>{esc(title)}<small>„Jak na górze, tak na dole” · Astrologia hermetyczna</small></h1>
</header>
<div class="meta">
  <span><b>A · {esc(nameA)}</b> · {esc(syn['meta']['dobA'])} · ☉ {esc(L[lang]['signs'][syn['meta']['sunA']])}</span>
  <span><b>B · {esc(nameB)}</b> · {esc(syn['meta']['dobB'])} · ☉ {esc(L[lang]['signs'][syn['meta']['sunB']])}</span>
</div>
<section class="duo">
  <div><h3>A · {esc(nameA)}</h3>{wheel_svg(A, lang)}{balance_bars(A, lang)}</div>
  <div><h3>B · {esc(nameB)}</h3>{wheel_svg(B, lang)}{balance_bars(B, lang)}</div>
</section>
{composite_section}
<section><h2>{esc(UI_SYN[lang]['interaspects'])}</h2>{scrollx(interaspect_table(syn, lang), UI_SYN[lang]['interaspects'])}</section>
<section><h2>{tip(UI_SYN[lang]['overlays'], 'dom', lang)}</h2>{overlay_lists(syn, lang, nameA, nameB)}</section>
<section class="reading" id="reading"><h2>{esc(u['reading'])}</h2>
{prose_html_all}{conf_html}</section>
<footer><p>{esc(u['tiphint'])}</p><p>{esc(disclaimer)}</p><p>{esc(u['generated'])}</p></footer>
</main></body></html>"""
    open(args.out, "w", encoding="utf-8", newline="\n").write(out)
    print(f"written {args.out} ({len(out)} bytes)")


if __name__ == "__main__":
    main()
