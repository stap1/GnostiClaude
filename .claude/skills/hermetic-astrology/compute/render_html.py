#!/usr/bin/env python3
"""
HTML exporter — turns chart_engine.py JSON (+ the reading.md prose) into a
single, self-contained, accessible HTML report: an SVG chart wheel, semantic
tables, balance bars, the hermetic signature, and the full interpretation.

Accessibility: semantic landmarks & headings, real <table> with <caption> and
<th scope>, aspect names spelled out in text (color is never the only carrier),
high-contrast palette, print stylesheet (light) for PDF export, lang attribute.

Usage:
  py -3.13 render_html.py chart.json --reading reading.md --lang pl \
      --out reading.html [--title "..."]
"""

import argparse
import datetime as dtm
import html
import json
import math
import re
import sys

from render_chart import L, PLANET_GLYPH, ASPECT_GLYPH, ROMAN, GRID_ORDER, TRAD, deg_str

SIGN_GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
SIGN_ELEMENT = ["fire", "earth", "air", "water"] * 3

ASPECT_NAME = {
    "en": {"Conjunction": "conjunction", "Opposition": "opposition",
           "Trine": "trine", "Square": "square", "Sextile": "sextile",
           "Quincunx": "quincunx", "Semisextile": "semisextile",
           "Semisquare": "semisquare", "Sesquiquadrate": "sesquiquadrate",
           "Quintile": "quintile"},
    "pl": {"Conjunction": "koniunkcja", "Opposition": "opozycja",
           "Trine": "trygon", "Square": "kwadratura", "Sextile": "sekstyl",
           "Quincunx": "kwinkunks", "Semisextile": "półsekstyl",
           "Semisquare": "półkwadratura", "Sesquiquadrate": "półtorakwadratura",
           "Quintile": "kwintyl"},
}
PHASE_WORD = {
    "en": {"applying": "applying", "separating": "separating",
           "exact": "exact", "—": "—"},
    "pl": {"applying": "aplikujący", "separating": "separujący",
           "exact": "dokładny", "—": "—"},
}
UI = {
    "en": {"positions": "Positions", "wheel_desc": "Natal chart wheel",
           "balance": "Element & modality balance", "dignity": "Dignity & condition",
           "aspect_grid": "Aspect grid", "aspect_list": "Key aspects (tightest first)",
           "signature": "Hermetic signature", "reading": "Interpretation",
           "confidence": "Confidence", "aspect": "Aspect", "orb": "Orb",
           "phase": "Phase", "generated": "Generated with the hermetic-astrology "
           "skill · Skyfield / JPL de421 · tropical zodiac",
           "tiphint": "Dotted-underlined terms hide short definitions — "
           "hover, tap, or focus them.",
           "skip": "Skip to interpretation",
           "nav_label": "Sections", "nav_wheel": "Wheel", "nav_pos": "Positions",
           "nav_dig": "Dignity", "nav_asp": "Aspects", "nav_houses": "Houses",
           "nav_sig": "Signature", "nav_read": "Reading",
           "nav_tozs": "Identity", "nav_mech": "Mechanism",
           "mech_title": "⚙ The chart's mechanism",
           "mech_hint": "Positions, dignities and the aspect grid — the "
           "movement behind the reading. Unfold to inspect the works.",
           "totop": "Back to top",
           "chip_ruler": "Chart ruler", "chip_elem": "Element",
           "chip_mode": "Mode", "chip_tight": "Tightest aspect",
           "def_label": "Definition", "def_close": "Close",
           "theme_label": "Toggle light/dark theme",
           "timeline": "Transit timeline", "nav_transits": "Timeline",
           "tl_legend": "Bar = the aspect’s working window (orb ≤ 3°), "
           "brighter core = orb ≤ 1°, ◆ = exact hit · ● new moon, "
           "○ full moon · dashed line = reading date.",
           "heat_hint": "Cell tint deepens as the orb tightens — "
           "stronger colour = closer aspect."},
    "pl": {"positions": "Pozycje", "wheel_desc": "Koło horoskopu",
           "balance": "Balans żywiołów i jakości", "dignity": "Godność i kondycja",
           "aspect_grid": "Siatka aspektów", "aspect_list":
           "Kluczowe aspekty (od najściślejszych)",
           "signature": "Sygnatura hermetyczna", "reading": "Interpretacja",
           "confidence": "Pewność", "aspect": "Aspekt", "orb": "Orb",
           "phase": "Faza", "generated": "Wygenerowano skillem hermetic-astrology "
           "· Skyfield / JPL de421 · zodiak tropikalny",
           "tiphint": "Hasła podkreślone kropkami kryją krótkie definicje — "
           "najedź kursorem, stuknij palcem lub ustaw fokus klawiaturą.",
           "skip": "Przejdź do interpretacji",
           "nav_label": "Sekcje", "nav_wheel": "Koło", "nav_pos": "Pozycje",
           "nav_dig": "Godność", "nav_asp": "Aspekty", "nav_houses": "Domy",
           "nav_sig": "Sygnatura", "nav_read": "Odczyt",
           "nav_tozs": "Tożsamość", "nav_mech": "Mechanizm",
           "mech_title": "⚙ Mechanizm karty",
           "mech_hint": "Pozycje, godności i siatka aspektów — praca trybów "
           "za odczytem. Rozwiń, by zajrzeć do werku.",
           "totop": "Na górę strony",
           "chip_ruler": "Władca karty", "chip_elem": "Żywioł",
           "chip_mode": "Jakość", "chip_tight": "Najściślejszy aspekt",
           "def_label": "Definicja", "def_close": "Zamknij",
           "theme_label": "Przełącz motyw jasny/ciemny",
           "timeline": "Oś czasu tranzytów", "nav_transits": "Oś czasu",
           "tl_legend": "Pas = okno działania aspektu (orb ≤ 3°), jaśniejszy "
           "rdzeń = orb ≤ 1°, ◆ = aspekt dokładny · ● nów, ○ pełnia · "
           "linia przerywana = data odczytu.",
           "heat_hint": "Tło komórki gęstnieje wraz z ciasnością orbu — "
           "mocniejszy kolor = ściślejszy aspekt."},
}

# ── Glossary: lay-friendly one-liners shown as hover/focus tooltips ──────────
GLOSS = {
    "pl": {
        "sekta": "Podział horoskopów na dzienne (Słońce nad horyzontem) i nocne. "
                 "Część planet działa łagodniej „w swojej” porze — jak ludzie "
                 "dzienni i nocni.",
        "dekany": "Każdy znak dzieli się na trzy 10-stopniowe „dekany”, każdy "
                  "z własnym planetarnym opiekunem — subtelniejszy odcień znaku.",
        "loty": "Wyliczane punkty (nie ciała niebieskie), z greckich kleroi — "
                "„losy”. ⊕ Los Fortuny — sprawy ciała i okoliczności, „co się "
                "przydarza”; ⊗ Los Ducha — sprawy woli i powołania, „co "
                "świadomie robisz z życiem”.",
        "wladca": "Planeta władająca znakiem ascendentu — „gospodarz” całej "
                  "karty. Jej znak, dom i kondycja pokazują, kto i skąd "
                  "prowadzi tę biografię.",
        "zywiol": "Ile punktów karty przypada na znaki Ognia (zapał), Ziemi "
                  "(konkret), Powietrza (myśl) i Wody (czucie) — ogólny "
                  "temperament. Chip pokazuje żywioł przeważający.",
        "jakosc": "Rozkład punktów karty między znaki kardynalne (inicjowanie), "
                  "stałe (utrwalanie) i zmienne (adaptacja) — styl działania. "
                  "Chip pokazuje jakość przeważającą.",
        "wezly": "Punkty przecięcia drogi Księżyca z drogą Słońca. ☊ Węzeł Płn. "
                 "— kierunek rozwoju; ☋ Węzeł Płd. — stare, wygodne koleiny.",
        "solar": "Bliskość planety do Słońca: „spalenie” osłabia, „cazimi” "
                 "(w samym sercu Słońca) wzmacnia, „pod promieniami” lekko "
                 "przyćmiewa, „wolny” — bez wpływu.",
        "godnosc": "Jak bardzo planeta jest „u siebie” w danym znaku: od "
                   "domicylu (pełnia sił) po wygnanie i upadek (działanie "
                   "pod prąd).",
        "punkty": "Tradycyjna punktacja siły planety (wg W. Lilly’ego): "
                  "Domicyl +5 · Wywyższenie +4 · Tryplicytet +3 · Termy +2 · "
                  "Oblicze +1 · Wygnanie −5 · Upadek −4 · Peregryn −5 "
                  "(minusy się sumują). Plus = planeta wspiera swoje tematy "
                  "z łatwością; minus = wymagają świadomej pracy.",
        "dom": "Dwanaście „scen życia” (I — ja, VII — partnerstwo, X — kariera "
               "itd.), wyznaczanych z miejsca i godziny urodzenia.",
        "orb": "Odchyłka od dokładnego kąta, w stopniach. Im mniejszy orb, "
               "tym silniej działa aspekt.",
        "faza": "Aplikujący — aspekt dopiero się domyka (narasta); separujący — "
                "już się rozchodzi (wygasa); dokładny — w szczycie.",
        "aspekt": "Znaczący kąt między planetami: trygon i sekstyl płyną "
                  "gładko, kwadratura i opozycja tworzą twórcze napięcie, "
                  "koniunkcja łączy siły.",
        "rx": "Retrogradacja — pozorny ruch wsteczny planety na niebie; jej "
              "tematy zwracają się do wewnątrz i wracają do poprawki.",
        "ascendent": "Znak wschodzący nad horyzontem w chwili urodzenia — "
                     "„maska”, temperament i sposób wchodzenia w świat.",
        "mc": "Medium Coeli — najwyższy punkt karty: powołanie, rola publiczna, "
              "szczyt drogi.",
        "dzienhodz": "Każdym dniem tygodnia i każdą godziną (liczoną od wschodu "
                     "Słońca) włada jedna z 7 planet — starożytny rytm czasu.",
        "Domicyl": "Planeta we własnym znaku — u siebie, pełnia możliwości.",
        "Wywyższenie": "Planeta jak gość honorowy — działa świetnie, czasem "
                       "z przesadą.",
        "Tryplicytet": "Planeta w sprzyjającym sobie żywiole — komfort działania.",
        "Termy": "Własny odcinek stopni w znaku (granice egipskie) — drobne, "
                 "ale realne wsparcie.",
        "Oblicze": "Własny dekan (10° znaku) — minimalne oparcie, „przyczółek”.",
        "Wygnanie": "Znak naprzeciw własnego — działanie pod prąd, kosztem "
                    "większego wysiłku.",
        "Upadek": "Znak naprzeciw wywyższenia — energia niedoceniona, wymaga "
                  "dojrzewania.",
        "Peregryn": "Bez żadnej godności — wędrowiec bez oparcia; siła zależy "
                    "od wsparcia innych planet.",
        "kompozyt": "Karta „środka” relacji: każdy punkt leży w połowie drogi "
                    "między planetami dwojga ludzi. Opisuje związek jako "
                    "osobny, trzeci byt.",
    },
    "en": {
        "sekta": "Charts divide into day (Sun above horizon) and night ones; "
                 "some planets work more smoothly in “their” half.",
        "dekany": "Each sign splits into three 10° “decans”, each with its own "
                  "planetary patron — a finer shade of the sign.",
        "loty": "Calculated points, not bodies (Greek kleroi, “lots”). "
                "⊕ Lot of Fortune — body & circumstance, what befalls you; "
                "⊗ Lot of Spirit — will & vocation, what you do with life.",
        "wladca": "The planet ruling the rising sign — the chart’s “host”. "
                  "Its sign, house and condition show who steers the story "
                  "and from where.",
        "zywiol": "How many chart points fall in Fire (drive), Earth "
                  "(practicality), Air (thought) and Water (feeling) signs — "
                  "the base temperament. The chip shows the leading element.",
        "jakosc": "Chart points across cardinal (initiating), fixed "
                  "(sustaining) and mutable (adapting) signs — the style of "
                  "action. The chip shows the leading mode.",
        "wezly": "Where the Moon’s path crosses the Sun’s. ☊ North Node — "
                 "growth direction; ☋ South Node — old comfortable ruts.",
        "solar": "Closeness to the Sun: “combust” weakens, “cazimi” (in the "
                 "Sun’s heart) empowers, “under beams” dims slightly.",
        "godnosc": "How much a planet is “at home” in a sign — from domicile "
                   "(full strength) to detriment and fall (uphill work).",
        "punkty": "Traditional strength score (Lilly): Domicile +5 · "
                  "Exaltation +4 · Triplicity +3 · Term +2 · Face +1 · "
                  "Detriment −5 · Fall −4 · Peregrine −5 (minuses stack). "
                  "Positive = effortless support; negative = conscious work "
                  "needed.",
        "dom": "Twelve “life stages” (I — self, VII — partnership, X — career…) "
               "set by birth place and time.",
        "orb": "Deviation from the exact angle, in degrees. Smaller orb = "
               "stronger aspect.",
        "faza": "Applying — still building; separating — already fading; "
                "exact — at peak.",
        "aspekt": "A meaningful angle between planets: trines/sextiles flow, "
                  "squares/oppositions create productive tension, conjunctions "
                  "merge forces.",
        "rx": "Retrograde — apparent backward motion; the planet’s themes turn "
              "inward for revision.",
        "ascendent": "The sign rising at birth — the “mask”, temperament, way "
                     "of meeting the world.",
        "mc": "Medium Coeli — the chart’s highest point: vocation and public "
              "role.",
        "dzienhodz": "Each weekday and each hour (counted from sunrise) is "
                     "ruled by one of the 7 planets — the ancient rhythm of time.",
        "Domicile": "A planet in its own sign — at home, full strength.",
        "Exaltation": "An honoured guest — works brilliantly, sometimes "
                      "excessively.",
        "Triplicity": "A planet in a friendly element — comfortable action.",
        "Term": "Its own degree-band in the sign — small but real support.",
        "Face": "Its own decan — a minimal foothold.",
        "Detriment": "The sign opposite its own — swimming upstream.",
        "Fall": "The sign opposite its exaltation — undervalued energy.",
        "Peregrine": "No dignity at all — a wanderer relying on other "
                     "planets’ support.",
        "kompozyt": "The relationship’s “midpoint” chart: every point lies "
                    "halfway between the two people’s planets — the couple "
                    "as a third entity.",
    },
}


def scrollx(inner, label=""):
    """Wrap a wide table in a horizontally scrollable, keyboard-reachable
    region so narrow (mobile) viewports scroll instead of overflowing."""
    aria = f" aria-label=\"{esc(label)}\"" if label else ""
    return f"<div class='scrollx' role='region'{aria} tabindex='0'>{inner}</div>"


def tip(label, key, lang):
    """Wrap a label in an accessible hover/focus tooltip from the glossary."""
    d = GLOSS[lang].get(key)
    if not d:
        return esc(label)
    return (f"<span class='tip' tabindex='0' data-tip=\"{esc(d)}\">"
            f"{esc(label)}</span>")


CSS = """
:root{
  color-scheme:dark;
  --bg:#10141f; --panel:#181e2e; --panel2:#1e2639; --ink:#e8e4d8;
  --muted:#a8a29a; --gold:#d4af6a; --gold-dim:#9c8250;
  --fire:#ff9e64; --earth:#9ece6a; --air:#7dcfff; --water:#7aa2f7;
  --hard:#f7768e; --soft:#73daca; --line:#333c52;
  --zebra:rgba(255,255,255,.025);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.65 Georgia,'Times New Roman',serif}
.glyph{font-family:'Segoe UI Symbol','Noto Sans Symbols 2','Segoe UI',sans-serif}
a{color:var(--gold)}
.skip{position:absolute;left:-999px;top:0;background:var(--gold);color:#111;
  padding:.5em 1em;z-index:9}
.skip:focus{left:8px}
main{max-width:1080px;margin:0 auto;padding:24px 20px 60px;
  position:relative;z-index:1}
/* ambient side ornaments — wide screens only, calm and non-interactive */
.amb-side{position:fixed;top:48px;bottom:0;width:calc((100vw - 1120px)/2);
  display:none;pointer-events:none;z-index:0;overflow:hidden;
  color:var(--gold)}
@media screen and (min-width:1300px){.amb-side{display:block}}
.amb-left{left:0}
.amb-right{right:0}
.ladder{position:absolute;inset:0;display:flex;flex-direction:column;
  justify-content:center;align-items:center;gap:6.5vh}
.ladder .lad{font-family:'Segoe UI Symbol','Noto Sans Symbols 2','Segoe UI',
  sans-serif;font-size:24px;opacity:.14;
  animation:ladfloat 11s ease-in-out infinite}
@keyframes ladfloat{0%,100%{transform:translateY(0);opacity:.09}
  50%{transform:translateY(-9px);opacity:.2}}
.amb-ring{position:absolute;top:50%;right:-190px;width:380px;height:380px;
  margin-top:-190px;opacity:.13}
.amb-ring circle{fill:none;stroke:currentColor}
.amb-ring text{fill:currentColor;font-size:15px;text-anchor:middle;
  dominant-baseline:central}
.amb-spin-a{animation:ospin 180s linear infinite;
  transform-origin:200px 200px}
.amb-spin-b{animation:ospin 260s linear infinite reverse;
  transform-origin:200px 200px}
header.title{text-align:center;border-bottom:1px solid var(--gold-dim);
  padding:28px 0 20px;margin-bottom:26px}
header.title .glyphs{color:var(--gold);letter-spacing:.5em;font-size:20px}
h1{font-size:30px;margin:.4em 0 .1em;color:var(--gold);font-weight:normal;
  letter-spacing:.08em}
h1 small{display:block;color:var(--muted);font-size:15px;letter-spacing:.15em;
  margin-top:6px;font-style:italic}
.meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
  gap:4px 28px;background:var(--panel);border:1px solid var(--line);
  border-radius:10px;padding:14px 20px;margin:0 0 28px;font-size:15px}
.meta b{color:var(--gold);font-weight:normal}
h2{color:var(--gold);font-weight:normal;letter-spacing:.06em;font-size:22px;
  border-bottom:1px solid var(--line);padding-bottom:6px;margin:44px 0 16px}
.wheelwrap{text-align:center}
.wheelwrap svg{max-width:820px;width:100%;height:auto;display:block;
  margin:0 auto}
.bars{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));
  gap:0 46px;max-width:760px;margin:18px auto 0}
.bar{display:grid;grid-template-columns:110px 1fr 2em;gap:10px;
  align-items:center;margin:7px 0;font-size:15px}
.bar .track{display:block;background:#252d42;border-radius:5px;height:16px;
  overflow:hidden}
.bar .fill{display:block;height:100%;border-radius:5px}
.f-fire{background:var(--fire)} .f-earth{background:var(--earth)}
.f-air{background:var(--air)} .f-water{background:var(--water)}
.f-mode{background:var(--gold)}
.scrollx{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:14px 0;
  border-radius:10px;scrollbar-width:thin;
  background:
    linear-gradient(90deg,var(--panel) 35%,rgba(0,0,0,0)) 0 0/48px 100%,
    linear-gradient(270deg,var(--panel) 35%,rgba(0,0,0,0)) 100% 0/48px 100%,
    linear-gradient(90deg,rgba(0,0,0,.5),rgba(0,0,0,0)) 0 0/16px 100%,
    linear-gradient(270deg,rgba(0,0,0,.5),rgba(0,0,0,0)) 100% 0/16px 100%,
    var(--panel);
  background-repeat:no-repeat;
  background-attachment:local,local,scroll,scroll,scroll}
.scrollx:focus-visible{outline:1px dotted var(--gold);outline-offset:2px}
.scrollx>table{margin:0;min-width:540px;background:transparent}
.scrollx th:first-child,.scrollx td:first-child{position:sticky;left:0;
  z-index:2;background:var(--panel);
  box-shadow:6px 0 8px -6px rgba(0,0,0,.45)}
.scrollx thead th:first-child{z-index:3;background:var(--panel2)}
.scrollx tbody tr:nth-child(even)>:not(:first-child){background:var(--zebra)}
table{border-collapse:separate;border-spacing:0;width:100%;margin:14px 0;
  font-size:15px;background:var(--panel);border-radius:10px}
thead th:first-child{border-top-left-radius:10px}
thead th:last-child{border-top-right-radius:10px}
caption{caption-side:top;text-align:left;color:var(--muted);font-style:italic;
  padding:4px 2px}
th,td{padding:8px 12px;text-align:left;border-bottom:1px solid var(--line)}
thead th{background:var(--panel2);color:var(--gold);font-weight:normal;
  letter-spacing:.05em}
tbody tr:last-child td{border-bottom:none}
td.num{font-variant-numeric:tabular-nums}
.dim-pos{color:var(--soft)} .dim-neg{color:var(--hard)}
.grid-tab td,.grid-tab th{text-align:center;padding:6px 8px;font-size:17px}
.asp-hard{color:var(--hard)} .asp-soft{color:var(--soft)}
.asp-conj{color:var(--gold)} .asp-minor{color:var(--muted)}
dl.sig{background:var(--panel);border:1px solid var(--gold-dim);
  border-radius:10px;padding:16px 22px;display:grid;
  grid-template-columns:max-content 1fr;gap:6px 18px;font-size:15.5px}
dl.sig dt{color:var(--gold)} dl.sig dd{margin:0}
.prose{max-width:74ch;margin-left:auto;margin-right:auto}
.prose p{margin:.65em 0;text-align:justify}
.prose p.item{padding-left:1.4em;text-indent:-1.4em}
section.reading h3{color:var(--gold);font-weight:normal;font-size:18px;
  margin:26px auto 8px;letter-spacing:.05em;max-width:74ch}
h4.sub{max-width:74ch;margin:24px auto 6px;text-align:center;
  color:var(--gold);font-weight:normal;font-size:15px;letter-spacing:.16em}
h4.sub::before{content:'· ';color:var(--gold-dim)}
h4.sub::after{content:' ·';color:var(--gold-dim)}
ul.conf{list-style:none;padding:14px 22px;background:var(--panel);
  border:1px solid var(--line);border-radius:10px;max-width:74ch;
  margin-left:auto;margin-right:auto}
footer{margin-top:46px;border-top:1px solid var(--gold-dim);padding-top:18px;
  color:var(--muted);font-style:italic;text-align:center;font-size:14.5px}
.tip{border-bottom:1px dotted var(--gold);cursor:help;position:relative}
.tip:hover::after,.tip:focus::after{content:attr(data-tip);position:absolute;
  left:0;top:1.7em;z-index:9;background:#0b0f18;color:var(--ink);
  border:1px solid var(--gold-dim);border-radius:9px;padding:10px 14px;
  width:330px;max-width:76vw;font-size:13.5px;line-height:1.55;
  font-style:normal;font-weight:normal;letter-spacing:0;text-align:left;
  text-indent:0;white-space:normal;box-shadow:0 8px 26px rgba(0,0,0,.55)}
.tip:focus{outline:1px dotted var(--gold);outline-offset:2px}

/* ── Tablet (≤ 900px): tighter rhythm, same layout ── */
@media screen and (max-width:900px){
  main{padding:20px 16px 48px}
  h1{font-size:26px}
  h2{font-size:20px;margin:38px 0 14px}
  .wheelwrap svg{max-width:640px}
}

/* ── Mobile (≤ 700px): single column, scrollable tables, tap tooltips ── */
@media screen and (max-width:700px){
  body{font-size:15px}
  main{padding:14px 10px 40px}
  header.title{padding:16px 0 12px;margin-bottom:16px}
  header.title .glyphs{letter-spacing:.28em;font-size:16px}
  h1{font-size:21px;letter-spacing:.04em}
  h1 small{font-size:12.5px;letter-spacing:.08em}
  h2{font-size:18px;margin:32px 0 12px}
  .meta{grid-template-columns:1fr;gap:3px 0;padding:10px 14px;font-size:14px}
  th,td{padding:6px 8px;font-size:13.5px}
  .grid-tab td,.grid-tab th{padding:4px 5px;font-size:14px}
  dl.sig{grid-template-columns:1fr;gap:1px 0;padding:12px 14px;font-size:14.5px}
  dl.sig dt{margin-top:9px}
  dl.sig dd{color:var(--ink)}
  .bar{grid-template-columns:88px 1fr 2em;gap:8px;font-size:13.5px}
  .bars{gap:0 24px}
  section.reading h3{font-size:16.5px}
  .prose p{text-align:left;hyphens:auto}
  ul.conf{padding:10px 14px;font-size:14px}
  footer{font-size:13px}
  /* tooltip becomes a fixed bottom sheet — reachable under the thumb */
  .tip:hover::after,.tip:focus::after{position:fixed;left:10px;right:10px;
    top:auto;bottom:10px;width:auto;max-width:none;font-size:14px}
}

/* ── UI v2 (2026-08): sticky nav + orrery, header sky, glossary sheet, chips ── */
html{scroll-behavior:smooth}
[id]{scroll-margin-top:72px}
.topbar{position:sticky;top:0;z-index:30;display:flex;align-items:center;gap:12px;
  background:rgba(16,20,31,.88);backdrop-filter:blur(10px);
  -webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line);
  padding:6px 12px}
.navlinks{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none;flex:1}
.navlinks::-webkit-scrollbar{display:none}
.navlinks a{color:var(--muted);text-decoration:none;white-space:nowrap;
  padding:7px 11px;border-radius:8px;font-size:14.5px;letter-spacing:.03em}
.navlinks a:hover,.navlinks a:focus-visible{color:var(--gold);background:var(--panel2)}
.progressbar{position:absolute;left:0;bottom:-1px;height:2px;width:0;
  background:linear-gradient(90deg,var(--gold-dim),var(--gold))}
.orrery{position:relative;flex:none;width:40px;height:40px;border:none;
  border-radius:50%;cursor:pointer;
  background:radial-gradient(circle,#232c47 0%,rgba(35,44,71,0) 70%)}
.orrery .sun{position:absolute;left:50%;top:50%;width:9px;height:9px;
  margin:-4.5px 0 0 -4.5px;border-radius:50%;background:var(--gold);
  box-shadow:0 0 9px 2px rgba(212,175,106,.75);
  animation:opulse 3.4s ease-in-out infinite}
.orrery .orbit{position:absolute;border-radius:50%;
  border:1px solid rgba(212,175,106,.25);animation:ospin linear infinite}
.orrery .o1{inset:8px;animation-duration:7s}
.orrery .o2{inset:2px;animation-duration:13s}
.orrery .pl{position:absolute;top:-3px;left:50%;margin-left:-2.5px;
  width:5px;height:5px;border-radius:50%}
.orrery .o1 .pl{background:#cfd6e4}
.orrery .o2 .pl{background:var(--soft)}
.orrery:hover .orbit,.orrery:focus-visible .orbit{animation-play-state:paused}
.orrery:focus-visible{outline:1px dotted var(--gold);outline-offset:2px}
@keyframes ospin{to{transform:rotate(360deg)}}
@keyframes opulse{50%{box-shadow:0 0 14px 4px rgba(212,175,106,.4)}}
header.title{position:relative;overflow:hidden}
.sky{position:absolute;inset:-40px;pointer-events:none;
  transition:transform .3s ease-out}
.zring{position:absolute;left:50%;top:50%;width:380px;height:380px;
  margin:-190px 0 0 -190px;opacity:.16;animation:ospin 240s linear infinite}
.zring text{fill:var(--gold);font-size:15px;text-anchor:middle;
  dominant-baseline:central}
.zring circle{fill:none;stroke:var(--gold-dim);stroke-width:.6}
.star{position:absolute;width:3px;height:3px;border-radius:50%;
  background:#e8e4d8;opacity:.5;animation:twinkle 4s ease-in-out infinite}
@keyframes twinkle{50%{opacity:.06;transform:scale(.6)}}
header.title h1,header.title .glyphs{position:relative;z-index:1}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 26px}
.chip{background:var(--panel2);border:1px solid var(--line);border-radius:999px;
  padding:5px 13px;font-size:13.5px;color:var(--ink)}
.chip b{color:var(--gold);font-weight:normal;margin-right:.45em}
.sbar{display:inline-block;vertical-align:middle;width:56px;height:7px;
  margin-left:8px;background:#252d42;border-radius:4px;overflow:hidden;
  position:relative}
.sbar::after{content:'';position:absolute;left:50%;top:0;bottom:0;width:1px;
  background:#4a5470}
.sbar i{position:absolute;top:0;bottom:0}
.sbar i.pos{background:var(--soft)}
.sbar i.neg{background:var(--hard)}
.dial{width:34px;height:19px;vertical-align:-3px;margin-left:7px}
.timeline{width:100%;height:auto;display:block}
.scrollx .timeline{min-width:840px}
.timeline text{font:12.5px Georgia,'Times New Roman',serif;fill:var(--ink)}
.timeline .tl-month{fill:var(--muted);font-style:italic}
.timeline .tl-date{font-size:10.5px;fill:var(--muted)}
.timeline .tl-grid{stroke:var(--line);stroke-width:1}
.timeline .tl-axis{stroke:var(--gold-dim);stroke-width:1}
.timeline rect.asp-conj{fill:var(--gold)}
.timeline rect.asp-hard{fill:var(--hard)}
.timeline rect.asp-soft{fill:var(--soft)}
.timeline rect.asp-minor{fill:var(--muted)}
.timeline .tl-exact{fill:var(--ink);stroke:var(--bg);stroke-width:1}
.timeline .tl-mark{stroke:var(--gold);stroke-dasharray:4 3;stroke-width:1.2}
.timeline .tl-new{fill:var(--gold)}
.timeline .tl-full{fill:var(--bg);stroke:var(--gold);stroke-width:1.5}
.tl-legend{color:var(--muted);font-size:13.5px;font-style:italic;
  margin:8px 2px 0}
/* skeleton: dane w prozie szeptem, werk przytłumiony do najechania */
.datum{font-size:.86em;color:var(--muted);
  font-variant-numeric:tabular-nums;transition:color .2s}
.prose p:hover .datum,.prose p:focus-within .datum{color:var(--ink)}
section#mechanizm>h2{cursor:pointer;position:relative;padding-right:34px;
  -webkit-user-select:none;user-select:none}
section#mechanizm>h2::after{content:'▾';position:absolute;right:8px;
  color:var(--gold-dim);transition:transform .2s}
section#mechanizm.closed>h2::after{transform:rotate(-90deg)}
section#mechanizm.closed>*:not(h2){display:none}
#mechanizm .scrollx{opacity:.8;filter:saturate(.7);
  transition:opacity .3s ease,filter .3s ease}
#mechanizm .scrollx:hover,#mechanizm .scrollx:focus-within{
  opacity:1;filter:none}
#mechanizm h3.mech-h3{color:var(--gold-dim);font-weight:normal;
  font-size:16.5px;letter-spacing:.05em;margin:26px 0 8px}
.mech-hint{color:var(--muted);font-style:italic;font-size:13.5px;
  margin:2px 0 10px}
@media print{section#mechanizm.closed>*{display:block}
  #mechanizm .scrollx{opacity:1;filter:none}}
.tipsheet{position:fixed;left:0;right:0;bottom:0;z-index:40;
  background:var(--panel);border-top:2px solid var(--gold-dim);
  box-shadow:0 -10px 30px rgba(0,0,0,.5);
  padding:14px 18px calc(16px + env(safe-area-inset-bottom, 0px));
  transform:translateY(110%);transition:transform .25s ease;
  max-height:45vh;overflow-y:auto}
.tipsheet.open{transform:translateY(0)}
.tipsheet .tiphead{display:flex;justify-content:space-between;
  align-items:center;gap:12px}
.tipsheet b{color:var(--gold);font-weight:normal;font-size:16px}
.tipsheet p{margin:.5em 0 0;font-size:15px;line-height:1.6}
.tipclose{background:none;border:1px solid var(--line);color:var(--muted);
  border-radius:8px;font-size:15px;padding:2px 10px;cursor:pointer}
.tipclose:hover{color:var(--gold);border-color:var(--gold-dim)}
@media (hover:none){.tip:hover::after,.tip:focus::after{display:none}}
@media screen and (max-width:700px){
  .topbar{padding:4px 8px;gap:8px}
  .navlinks a{padding:6px 8px;font-size:13.5px}
  .zring{width:300px;height:300px;margin:-150px 0 0 -150px}
  .chip{font-size:12.5px;padding:4px 10px}
}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  .orrery .orbit,.orrery .sun,.zring,.star{animation:none}
  .ladder .lad,.amb-spin-a,.amb-spin-b{animation:none}
  .sky{transition:none}
}

/* ── Light theme (toggle in the topbar; persisted in localStorage) ── */
:root[data-theme=light]{color-scheme:light;
  --bg:#f4efe4;--panel:#fbf8f0;--panel2:#efe6d2;--ink:#292521;--muted:#6c655a;
  --gold:#8a6a25;--gold-dim:#a8862f;--line:#d9d0bc;
  --fire:#c05621;--earth:#3f7d2c;--air:#1c6ea4;--water:#3949ab;
  --hard:#b3324b;--soft:#0e7568;--zebra:rgba(0,0,0,.03)}
[data-theme=light] .topbar{background:rgba(244,239,228,.92)}
[data-theme=light] .bar .track,[data-theme=light] .sbar{background:#e3dac5}
[data-theme=light] .sbar::after{background:#b9ae95}
[data-theme=light] .star{background:#a8862f}
[data-theme=light] .zring{opacity:.22}
[data-theme=light] .orrery{
  background:radial-gradient(circle,#efe6d2 0%,rgba(239,230,210,0) 70%)}
[data-theme=light] .tip:hover::after,[data-theme=light] .tip:focus::after{
  background:#fffdf7;box-shadow:0 8px 26px rgba(90,75,40,.28)}
.themebtn{flex:none;background:none;border:1px solid var(--line);
  color:var(--gold);border-radius:50%;width:34px;height:34px;cursor:pointer;
  font-size:17px;line-height:1;display:flex;align-items:center;
  justify-content:center;padding:0}
.themebtn:hover{border-color:var(--gold-dim);background:var(--panel2)}
.themebtn:focus-visible{outline:1px dotted var(--gold);outline-offset:2px}

/* ── Mobile accordion: h2 headers fold their sections (JS adds .acc/.tog) ── */
@media screen and (max-width:700px){
  body.acc main>section.tog>h2{cursor:pointer;position:relative;
    padding-right:34px;-webkit-user-select:none;user-select:none}
  body.acc main>section.tog>h2::after{content:'▾';position:absolute;right:8px;
    color:var(--gold-dim);transition:transform .2s}
  body.acc main>section.tog.closed>h2::after{transform:rotate(-90deg)}
  body.acc main>section.tog.closed>h2{margin-bottom:0}
  body.acc main>section.tog.closed>:not(h2){display:none}
}
@media print{.topbar,.tipsheet,.sky,.themebtn,.amb-side{display:none}}
@media print{.tip{border-bottom:none}}
@media print{
  :root{color-scheme:light;
    --bg:#fff;--panel:#fff;--panel2:#f3efe6;--ink:#1c1c1c;--muted:#555;
    --gold:#7a5c1e;--gold-dim:#7a5c1e;--line:#ccc;
    --fire:#c05621;--earth:#38761d;--air:#1c6ea4;--water:#3949ab;
    --hard:#b91c1c;--soft:#0f766e}
  body{font-size:12.5px}
  .wheelwrap svg{max-width:520px}
  .scrollx{overflow:visible}
  .scrollx>table{min-width:0}
  h2{page-break-after:avoid}
  table,dl.sig,.wheelwrap{page-break-inside:avoid}
}
"""


def esc(s):
    return html.escape(str(s), quote=True)


# ─────────────────────────────────────────────────────────────────────────────
# SVG wheel
# ─────────────────────────────────────────────────────────────────────────────


def wheel_svg(chart, lang, houseless=False):
    """Chart wheel. Radial layout (C=450, viewBox 900):
    430/380 sign ring · 380-369 tick band · 335/302/269 staggered planet
    glyphs with haloed degree labels at glyph-26 · 218/190 house-number band
    · chords inside r=186.

    houseless=True draws the same wheel with no cusps, house numbers or
    AC/MC labels and orients it to 0° Aries — for charts whose birth time
    is unknown, where those would be fabricated precision."""
    asc = chart["angles"]["Ascendant"]["lon"]
    mc = chart["angles"]["Midheaven"]["lon"]
    cusps = chart["house_cusps"]
    planets = chart["planets"]
    lots = chart.get("lots", {})
    C = 450
    origin = 0.0 if houseless else asc

    def xy(lon, r):
        th = math.radians(180.0 - (lon - origin))
        return C + r * math.cos(th), C + r * math.sin(th)

    def line(lon, r1, r2, cls, wdt=1.0, extra=""):
        x1, y1 = xy(lon, r1)
        x2, y2 = xy(lon, r2)
        return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"'
                f' class="{cls}" stroke-width="{wdt}"{extra}/>')

    ecol = {"fire": "var(--fire)", "earth": "var(--earth)",
            "air": "var(--air)", "water": "var(--water)"}
    s = []
    for r in (430, 380, 218, 190):
        s.append(f'<circle cx="{C}" cy="{C}" r="{r}" class="ring"/>')

    # sign ring: boundaries, colored glyphs, 5°/10° tick band
    for i in range(12):
        s.append(line(i * 30, 380, 430, "spoke", 1.2))
        gx, gy = xy(i * 30 + 15, 405)
        s.append(f'<text x="{gx:.1f}" y="{gy:.1f}" class="signglyph" '
                 f'fill="{ecol[SIGN_ELEMENT[i]]}">{SIGN_GLYPHS[i]}</text>')
    for d in range(0, 360, 5):
        s.append(line(d, 380, 374 if d % 10 else 369, "tick", 0.7))

    # house cusps + numbers in the inner band
    if not houseless:
        for i, cusp in enumerate(cusps):
            axis = i in (0, 3, 6, 9)
            s.append(line(cusp, 190, 380, "cusp" + (" axis" if axis else ""),
                          2.6 if axis else 0.8))
            hx, hy = xy((cusp + ((cusps[(i + 1) % 12] - cusp) % 360) / 2), 204)
            s.append(f'<text x="{hx:.1f}" y="{hy:.1f}" class="hnum halo">{ROMAN[i]}</text>')

        # AC / MC labels on the axes, inside the sign band, haloed
        for lon, lab in ((asc, "AC"), (mc, "MC")):
            lx, ly = xy(lon, 397)
            s.append(f'<text x="{lx:.1f}" y="{ly:.1f}" class="axis-lab halo">{lab}</text>')

    # planets + lots, radially staggered when angularly crowded
    order = [k for k in GRID_ORDER + ["South Node"] if k in planets]
    plist = sorted((planets[k]["lon"], k, False) for k in order)
    for lname, lo in lots.items():
        plist.append((lo["lon"], lname, True))
    plist.sort()
    level, prev = 0, None
    ppos = {}
    for lon, k, is_lot in plist:
        level = (level + 1) % 3 if prev is not None and (lon - prev) < 8 else 0
        ppos[k] = (lon, 335 - level * 33, is_lot)
        prev = lon
    # three passes so labels are never hidden under later-drawn glyphs:
    # ticks & guides, then glyphs, then Rx + degree labels on top
    glyphs_pass, labels_pass = [], []
    for k, (lon, r, is_lot) in ppos.items():
        src = lots[k] if is_lot else planets[k]
        s.append(line(lon, 371, 380, "ptick", 1.6))
        s.append(line(lon, r + 17, 369, "guide", 0.6))
        px, py = xy(lon, r)
        cls = "lglyph" if is_lot else "pglyph"
        glyphs_pass.append(f'<text x="{px:.1f}" y="{py:.1f}" class="{cls} halo">'
                           f'{PLANET_GLYPH[k]}</text>')
        if src.get("retrograde"):
            labels_pass.append(f'<text x="{px + 14:.1f}" y="{py - 12:.1f}" '
                               f'class="rx halo">Rx</text>')
        dx, dy = xy(lon, r - 26)
        labels_pass.append(f'<text x="{dx:.1f}" y="{dy:.1f}" class="pdeg halo">'
                           f'{deg_str(src["position"])}</text>')
    s += glyphs_pass + labels_pass

    # aspect chords (majors between planets; conjunctions show as clusters)
    for a in chart["aspects"]:
        if a["angle"] not in (60, 90, 120, 180):
            continue
        if a["a"] not in ppos or a["b"] not in ppos:
            continue
        cls = "asp-hard" if a["angle"] in (90, 180) else "asp-soft"
        x1, y1 = xy(ppos[a["a"]][0], 186)
        x2, y2 = xy(ppos[a["b"]][0], 186)
        w = 2.6 if a["orb"] < 2 else 1.2
        op = 0.9 if a["orb"] < 2 else 0.45
        t = L[lang]
        chord_tip = (f"{t['planets'].get(a['a'], a['a'])} "
                     f"{ASPECT_NAME[lang][a['aspect']]} "
                     f"{t['planets'].get(a['b'], a['b'])} · {a['orb']:.1f}° · "
                     f"{PHASE_WORD[lang].get(a['phase'], a['phase'])}")
        s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"'
                 f' class="chord {cls}" stroke-width="{w}" opacity="{op}">'
                 f'<title>{esc(chord_tip)}</title></line>')

    style = """
    .ring{fill:none;stroke:var(--gold-dim);stroke-width:1.4}
    .spoke,.tick{stroke:var(--line)} .cusp{stroke:var(--gold-dim)}
    .cusp.axis{stroke:var(--gold)} .ptick{stroke:var(--ink)}
    .guide{stroke:var(--muted);opacity:.35}
    .halo{paint-order:stroke;stroke:var(--bg);stroke-width:4px;
      stroke-linejoin:round}
    .signglyph{font-size:34px;text-anchor:middle;dominant-baseline:central;
      font-family:'Segoe UI Symbol','Noto Sans Symbols 2',sans-serif}
    .pglyph{font-size:30px;fill:var(--ink);text-anchor:middle;
      dominant-baseline:central;
      font-family:'Segoe UI Symbol','Noto Sans Symbols 2',sans-serif}
    .lglyph{font-size:22px;fill:var(--gold);text-anchor:middle;
      dominant-baseline:central;
      font-family:'Segoe UI Symbol','Noto Sans Symbols 2',sans-serif}
    .rx{font-size:12px;fill:var(--hard);text-anchor:middle;font-weight:bold}
    .pdeg{font-size:13px;fill:var(--ink);text-anchor:middle;
      dominant-baseline:central;opacity:.92}
    .hnum{font-size:13px;fill:var(--muted);text-anchor:middle;
      dominant-baseline:central}
    .axis-lab{font-size:17px;fill:var(--gold);text-anchor:middle;
      dominant-baseline:central;font-weight:bold}
    .chord.asp-hard{stroke:var(--hard)} .chord.asp-soft{stroke:var(--soft)}
    .chord{pointer-events:stroke;cursor:help;
      transition:stroke-width .15s,opacity .15s}
    .chord:hover{stroke-width:4.2;opacity:1}
    """
    desc = ({"pl": "Koło horoskopu bez domów — godzina urodzenia nieznana",
             "en": "Chart wheel without houses — birth time unknown"}[lang]
            if houseless else
            f"{UI[lang]['wheel_desc']}: AC {chart['angles']['Ascendant']['position']}, "
            f"MC {chart['angles']['Midheaven']['position']}")
    return (f'<svg viewBox="0 0 900 900" role="img" aria-label="{esc(desc)}">'
            f"<style>{style}</style><title>{esc(desc)}</title>"
            + "".join(s) + "</svg>")


# ─────────────────────────────────────────────────────────────────────────────
# HTML sections
# ─────────────────────────────────────────────────────────────────────────────


def degree_dial(deg):
    """Mini 0–30° gauge next to the degree text: a semicircular arc whose
    needle shows how deep in its sign the point stands. Degrees on a sign
    boundary (<1° or >29°) get the warning colour."""
    th = math.radians(180 * min(max(deg, 0.0), 30.0) / 30)
    x, y = 18 - 14 * math.cos(th), 18 - 14 * math.sin(th)
    col = "var(--hard)" if (deg < 1 or deg > 29) else "var(--gold)"
    return (f"<svg class='dial' viewBox='0 0 36 20' aria-hidden='true'>"
            f"<path d='M4 18 A14 14 0 0 1 32 18' fill='none' "
            f"stroke='var(--line)' stroke-width='2'/>"
            f"<circle cx='11' cy='5.9' r='1' fill='#4a5470'/>"
            f"<circle cx='25' cy='5.9' r='1' fill='#4a5470'/>"
            f"<line x1='18' y1='18' x2='{x:.1f}' y2='{y:.1f}' "
            f"stroke='{col}' stroke-width='1.6'/>"
            f"<circle cx='{x:.1f}' cy='{y:.1f}' r='2' fill='{col}'/></svg>")


def house_of(lon, cusps):
    """Whole-sign/quadrant house of a longitude from the chart's cusps.
    Needed for the MC row: in Whole Sign the MC can fall in IX–XI."""
    for i in range(12):
        c1, c2 = cusps[i], cusps[(i + 1) % 12]
        span = (c2 - c1) % 360.0 or 360.0
        if (lon - c1) % 360.0 < span:
            return i + 1
    return 10


def positions_table(chart, lang):
    t, u = L[lang], UI[lang]
    rows = []
    for k in GRID_ORDER + ["South Node"]:
        if k not in chart["planets"]:
            continue
        p = chart["planets"][k]
        dg = ", ".join(t["dign"][d] for d in p.get("dignities", [])) or "—"
        sc = p.get("dignity_score")
        cls = "dim-pos" if (sc or 0) > 0 else "dim-neg" if (sc or 0) < 0 else ""
        dcell = f'<span class="{cls}">{esc(dg)}{f" ({sc:+d})" if sc is not None else ""}</span>'
        rows.append(
            f"<tr><th scope=\"row\"><span class='glyph'>{PLANET_GLYPH[k]}</span> "
            f"{esc(t['planets'][k])}</th>"
            f"<td><span class='glyph'>{p['sign_glyph']}</span> {esc(t['signs'][p['sign']])}</td>"
            f"<td class='num'>{esc(deg_str(p['position']))}"
            f"{degree_dial(p.get('deg_in_sign', p['lon'] % 30))}</td>"
            f"<td class='num'>{ROMAN[p['house'] - 1]}</td><td>{dcell}</td>"
            f"<td>{'Rx' if p.get('retrograde') else ''}</td></tr>")
    for k in ("Ascendant", "Midheaven"):
        a = chart["angles"][k]
        gkey = "ascendent" if k == "Ascendant" else "mc"
        rows.append(
            f"<tr><th scope=\"row\">{PLANET_GLYPH[k]} "
            f"{tip(t['planets'][k], gkey, lang)}</th>"
            f"<td><span class='glyph'>{a['sign_glyph']}</span> {esc(t['signs'][a['sign']])}</td>"
            f"<td class='num'>{esc(deg_str(a['position']))}{degree_dial(a['lon'] % 30)}</td>"
            f"<td class='num'>{ROMAN[house_of(a['lon'], chart['house_cusps']) - 1]}</td>"
            f"<td>{esc(t['labels']['ruler'])}: {esc(t['planets'][a['ruler']])}</td>"
            f"<td></td></tr>")
    h = t["hdr"]
    return (f"<table><thead><tr>"
            f"<th scope='col'>{esc(h['body'])}</th><th scope='col'>{esc(h['sign'])}</th>"
            f"<th scope='col'>{esc(h['deg'])}</th>"
            f"<th scope='col'>{tip(h['hse'], 'dom', lang)}</th>"
            f"<th scope='col'>{tip(h['dign'], 'godnosc', lang)}</th>"
            f"<th scope='col'>{tip(h['mot'], 'rx', lang)}</th>"
            f"</tr></thead><tbody>{''.join(rows)}</tbody></table>")


def balance_bars(chart, lang):
    t = L[lang]
    out = ['<div class="bars">']
    for k in ("Fire", "Earth", "Air", "Water"):
        n = chart["balance"]["elements"][k]
        out.append(
            f'<div class="bar"><span>{esc(t["elements"][k])}</span>'
            f'<span class="track"><span class="fill f-{k.lower()}" '
            f'style="width:{n / 12 * 100:.0f}%"></span></span><b>{n}</b></div>')
    for k in ("Cardinal", "Fixed", "Mutable"):
        n = chart["balance"]["modalities"][k]
        out.append(
            f'<div class="bar"><span>{esc(t["modes"][k])}</span>'
            f'<span class="track"><span class="fill f-mode" '
            f'style="width:{n / 12 * 100:.0f}%"></span></span><b>{n}</b></div>')
    out.append("</div>")
    return "".join(out)


def dignity_table(chart, lang):
    t, u = L[lang], UI[lang]
    h = t["hdr"]
    rows = []
    for k in TRAD:
        p = chart["planets"][k]
        sc = p.get("dignity_score", 0)
        cls = "dim-pos" if sc > 0 else "dim-neg" if sc < 0 else ""
        digs = p.get("dignities", [])
        # each dignity name carries its own lay definition (EN keys = raw names)
        dcell = (" + ".join(
            tip(t["dign"][d], t["dign"][d] if lang == "pl" else d, lang)
            for d in digs) or "—")
        half = min(abs(sc), 10) * 5  # score −10..+10 → % of the mini-bar half
        sbar = ("<span class='sbar' aria-hidden='true'>"
                + (f"<i class='pos' style='left:50%;width:{half}%'></i>" if sc > 0
                   else f"<i class='neg' style='right:50%;width:{half}%'></i>" if sc < 0
                   else "")
                + "</span>")
        rows.append(
            f"<tr><th scope='row'><span class='glyph'>{PLANET_GLYPH[k]}</span> "
            f"{esc(t['planets'][k])}</th>"
            f"<td>{dcell}</td>"
            f"<td class='num {cls}'>{sc:+d}{sbar}</td>"
            f"<td>{esc(t['sect'].get(p.get('sect_status', ''), '—'))}</td>"
            f"<td>{esc(t['solar'].get(p.get('solar_condition', ''), '—')) if k != 'Sun' else '—'}</td></tr>")
    return (f"<table><thead><tr>"
            f"<th scope='col'>{esc(h['planet'])}</th>"
            f"<th scope='col'>{tip(h['essential'], 'godnosc', lang)}</th>"
            f"<th scope='col'>{tip(h['score'], 'punkty', lang)}</th>"
            f"<th scope='col'>{tip(h['sect'], 'sekta', lang)}</th>"
            f"<th scope='col'>{tip(h['solar'], 'solar', lang)}</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>")


def aspect_cls(angle):
    if angle == 0:
        return "asp-conj"
    if angle in (90, 180):
        return "asp-hard"
    if angle in (60, 120):
        return "asp-soft"
    return "asp-minor"


HEAT_RGB = {"asp-conj": "212,175,106", "asp-hard": "247,118,142",
            "asp-soft": "115,218,202", "asp-minor": "168,162,154"}


def heat_style(a):
    """Heat-map tint for an aspect-grid cell: the aspect-family colour at an
    opacity that grows as the orb tightens (0° ≈ .45, fading out by ~9°)."""
    alpha = max(0.03, (1.0 - min(a["orb"], 9.0) / 9.0) * 0.45)
    return f" style='background:rgba({HEAT_RGB[aspect_cls(a['angle'])]},{alpha:.2f})'"


def aspect_grid(chart, lang):
    u = UI[lang]
    amap = {frozenset((a["a"], a["b"])): a for a in chart["aspects"]}
    grid = [k for k in GRID_ORDER if k in chart["planets"]]
    head = "".join(f"<th scope='col'><span class='glyph'>{PLANET_GLYPH[k]}</span></th>"
                   for k in grid[:-1])
    rows = []
    for i in range(1, len(grid)):
        cells = []
        for j in range(i):
            a = amap.get(frozenset((grid[i], grid[j])))
            if a:
                nm = ASPECT_NAME[lang][a["aspect"]]
                cells.append(f"<td{heat_style(a)}><span class='glyph {aspect_cls(a['angle'])}' "
                             f"title='{esc(nm)} {a['orb']:.1f}°'>"
                             f"{ASPECT_GLYPH[a['aspect']]}</span></td>")
            else:
                cells.append("<td>·</td>")
        cells += ["<td></td>"] * (len(grid) - 1 - i)
        rows.append(f"<tr><th scope='row'><span class='glyph'>"
                    f"{PLANET_GLYPH[grid[i]]}</span></th>{''.join(cells)}</tr>")
    return (f"<table class='grid-tab'>"
            f"<caption>{esc(u['heat_hint'])}</caption>"
            f"<thead><tr><th></th>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>")


def aspect_list(chart, lang, limit=14):
    t, u = L[lang], UI[lang]
    rows, shown = [], 0
    for a in chart["aspects"]:
        if a["angle"] not in (0, 60, 90, 120, 150, 180) and shown >= 6:
            continue
        na = t["planets"].get(a["a"], a["a"])
        nb = t["planets"].get(a["b"], a["b"])
        nm = ASPECT_NAME[lang][a["aspect"]]
        rows.append(
            f"<tr><td><span class='glyph'>{PLANET_GLYPH.get(a['a'], '')}</span> {esc(na)}</td>"
            f"<td><span class='glyph {aspect_cls(a['angle'])}'>"
            f"{ASPECT_GLYPH[a['aspect']]}</span> {esc(nm)}</td>"
            f"<td><span class='glyph'>{PLANET_GLYPH.get(a['b'], '')}</span> {esc(nb)}</td>"
            f"<td class='num'>{a['orb']:.1f}°</td>"
            f"<td>{esc(PHASE_WORD[lang].get(a['phase'], a['phase']))}</td></tr>")
        shown += 1
        if shown >= limit:
            break
    return (f"<table><caption>{esc(u['aspect_list'])}</caption><thead><tr>"
            f"<th scope='col'></th>"
            f"<th scope='col'>{tip(u['aspect'], 'aspekt', lang)}</th>"
            f"<th scope='col'></th>"
            f"<th scope='col'>{tip(u['orb'], 'orb', lang)}</th>"
            f"<th scope='col'>{tip(u['phase'], 'faza', lang)}</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>")


def signature_panel(chart, lang):
    t, u = L[lang], UI[lang]
    herm, planets, lots = chart["hermetica"], chart["planets"], chart.get("lots", {})
    sect = chart["meta"]["sect"]
    items = []
    sect_word = t["labels"]["day_chart"] if sect == "day" else t["labels"]["night_chart"]
    items.append((t["labels"]["sect_l"],
                  f"{sect_word} ({'♃ ♄ ☉' if sect == 'day' else '☽ ♀ ♂'})"))
    items.append((t["labels"]["dayhour"],
                  f"{t['days'].get(herm.get('day_of_week', ''), '')} · "
                  f"{t['labels']['day_of']} {t['planets'][herm['planetary_day_ruler']]}"
                  + (f" · {t['labels']['hour_of']} "
                     f"{t['planets'][herm['planetary_hour_ruler']]} "
                     f"({herm['planetary_hour_index']})"
                     if herm.get("planetary_hour_ruler") else "")))
    dec = " · ".join(f"{g} {t['planets'][planets[k]['face_ruler']]}"
                     for k, g in (("Sun", "☉"), ("Moon", "☽"))
                     if planets[k].get("face_ruler"))
    items.append((t["labels"]["decans"], dec))
    if lots:
        items.append((t["labels"]["lots"], " · ".join(
            f"{PLANET_GLYPH[n]} {t['planets'][n]} {deg_str(lo['position'])} "
            f"{t['signs'][lo['sign']]} ({ROMAN[lo['house'] - 1]})"
            for n, lo in (("Fortune", lots.get("Fortune")),
                          ("Spirit", lots.get("Spirit"))) if lo)))
    sol = " · ".join(f"{PLANET_GLYPH[k]} {t['solar'][planets[k]['solar_condition']]}"
                     for k in TRAD if k != "Sun"
                     and planets[k].get("solar_condition") not in (None, "free"))
    items.append((t["labels"]["solar_l"], sol or t["labels"]["all_free"]))
    nn, sn = planets["North Node"], planets["South Node"]
    items.append((t["labels"]["nodes"],
                  f"☊ {t['signs'][nn['sign']]} ({ROMAN[nn['house'] - 1]}) — "
                  f"{t['labels']['growth']} ←→ ☋ {t['signs'][sn['sign']]} "
                  f"({ROMAN[sn['house'] - 1]}) — {t['labels']['release']}"))
    gkey = {t["labels"]["sect_l"]: "sekta", t["labels"]["dayhour"]: "dzienhodz",
            t["labels"]["decans"]: "dekany", t["labels"]["lots"]: "loty",
            t["labels"]["solar_l"]: "solar", t["labels"]["nodes"]: "wezly"}
    body = "".join(
        f"<dt>{tip(k, gkey.get(k, ''), lang)}</dt><dd>{esc(v)}</dd>"
        for k, v in items)
    return f"<dl class='sig' aria-label='{esc(u['signature'])}'>{body}</dl>"


# ─────────────────────────────────────────────────────────────────────────────
# Reading prose extraction
# ─────────────────────────────────────────────────────────────────────────────

BOXCHARS = set("│┌└├╞╔╚║═╪┼┤╡┬┴┐┘╗╝")
MARKER = re.compile(
    r"^([☉☽☿♀♂♃♄♅♆♇⊕⊗]|AC |MC |SYNTEZA|SYNTHESIS|KLUCZ|KEY|KONFIGURACJE|"
    r"CONFIGURATIONS|NAGŁÓWEK|→|„|[IVX]{1,4}\s{2,}|[IVX]{2,4}\s+|\d\.\s)")


def is_art(l):
    st = l.strip()
    if not st:
        return False
    if l[0] in BOXCHARS or st[0] in BOXCHARS:
        return True
    if "█" in l or "░" in l:
        return True
    if set(st) <= {"─"}:
        return True
    if st.startswith("☌ 0°") or st.startswith("cazimi"):
        return True
    if st.startswith("Kluczowe aspekty") or st.startswith("Key aspects"):
        return True
    if re.match(r"^\s*[☉☽☿♀♂♃♄♅♆♇☊]", l) and len(l.rstrip()) < 50:
        return True  # aspect-grid / aspect-list rows (short); prose lines are longer
    return False


def extract_prose(text):
    sections, cur, conf = [], None, []
    for ln in text.splitlines():
        m = re.match(r"^─── (.+?) ─+\s*$", ln)
        if m:
            cur = (m.group(1).strip(), [])
            sections.append(cur)
            continue
        if ln.startswith("│") and cur and cur[0].startswith("8"):
            conf.append(ln.lstrip("│ ").rstrip())
        if cur:
            cur[1].append(ln)
    out = []
    for title, ls in sections:
        paras, buf, skip = [], [], False
        for l in ls:
            if not l.strip():
                skip = False
                if buf:
                    paras.append(buf)
                    buf = []
                continue
            # "Key aspects" datum blocks are re-rendered natively; drop the
            # whole paragraph, not just the first line
            if l.strip().startswith(("Kluczowe aspekty", "Key aspects")):
                skip = True
            if skip or is_art(l):
                continue
            if buf and not l.startswith("  ") and MARKER.match(l.lstrip()):
                paras.append(buf)
                buf = []
            buf.append(l)
        if buf:
            paras.append(buf)
        texts = [" ".join(x.strip() for x in p) for p in paras]
        # re-join words hyphenated across source line breaks
        texts = [re.sub(r"([a-ząćęłńóśźż])- ([a-ząćęłńóśźż])", r"\1\2", p)
                 for p in texts if p]
        # drop the disclaimer (re-rendered natively in the footer). MARKER
        # splits its closing motto onto its own paragraph — drop that too, so
        # section 8 ends on its Nag Hammadi closer, not on the motto.
        texts = [p for p in texts
                 if not p.startswith(("Ten odczyt", "This reading"))
                 and not p.lstrip("„“\"").startswith(("Jak na górze, tak na dole",
                                                      "As above, so below"))]
        if texts:
            out.append((title, texts))
    conf = [c for c in conf if c and not set(c) <= {"─"}]
    return out, conf


SUB_RE = re.compile(r"^·\s*(.+?)\s*·\s*(.*)$", re.S)
ABBREV = {"np", "ok", "tzw", "itd", "itp", "tj", "in", "m.in", "por", "r",
          "w", "ww", "cd", "vs", "st", "godz", "e.g", "i.e", "cf", "etc"}


def split_long(p, limit=550, chunk=430):
    """Split an over-long paragraph at sentence ends into ~chunk-sized parts
    (readability; never inside abbreviations or numeric dates)."""
    if len(p) <= limit:
        return [p]
    sents, last = [], 0
    for m in re.finditer(r"\.\s+(?=[0-9A-ZĄĆĘŁŃÓŚŹŻ„“(])", p):
        w = p[last:m.start()].rsplit(" ", 1)[-1].rstrip(".").lower()
        if w in ABBREV or len(w) <= 1:
            continue
        sents.append(p[last:m.end()].rstrip())
        last = m.end()
    sents.append(p[last:])
    out, buf = [], ""
    for s in sents:
        if buf and len(buf) + len(s) > chunk:
            out.append(buf)
            buf = s
        else:
            buf = f"{buf} {s}".strip()
    if buf:
        out.append(buf)
    return out


DATUM_RE = re.compile(r"(\d+°(?:\d+′)?|\d+[.,]\d+°)")


def mute_datums(escaped):
    """Wrap degree/orb figures in a quiet span — the skeleton-watch rule:
    precision stays present in the prose but whispers."""
    return DATUM_RE.sub(r"<span class='datum'>\1</span>", escaped)


def prose_html(paras):
    out = []
    for p in paras:
        m = SUB_RE.match(p)
        if m:  # "· SUBHEAD ·" marker → a small centred subheading
            out.append(f"<h4 class='sub'>{esc(m.group(1))}</h4>")
            p = m.group(2).strip()
            if not p:
                continue
        if MARKER.match(p):
            out.append(f"<p class='item'>{mute_datums(esc(p))}</p>")
        else:
            out.extend(f"<p>{mute_datums(esc(c))}</p>" for c in split_long(p))
    return f"<div class='prose'>{''.join(out)}</div>"


# ─────────────────────────────────────────────────────────────────────────────
# UI v2 pieces: header sky, summary chips, top navigation, interaction script
# ─────────────────────────────────────────────────────────────────────────────

ZODIAC_GLYPHS = "♈♉♊♋♌♍♎♏♐♑♒♓"


def header_sky():
    """Decorative animated sky behind the title: a slowly rotating zodiac
    ring and a handful of twinkling stars (pure CSS animations)."""
    ring = ['<svg class="zring" viewBox="0 0 200 200" aria-hidden="true">',
            '<circle cx="100" cy="100" r="97"/>',
            '<circle cx="100" cy="100" r="76"/>']
    for i, g in enumerate(ZODIAC_GLYPHS):
        a = math.radians(i * 30 - 90)
        ring.append(f'<text x="{100 + 86.5 * math.cos(a):.1f}" '
                    f'y="{100 + 86.5 * math.sin(a):.1f}">{g}</text>')
    ring.append("</svg>")
    stars = [(7, 18, 0.0), (16, 64, 1.3), (28, 35, 2.1), (45, 80, 0.7),
             (60, 22, 2.9), (72, 58, 1.7), (84, 30, 0.4), (93, 70, 2.4),
             (38, 12, 3.1), (55, 50, 1.1)]
    star_html = "".join(
        f'<span class="star" style="left:{x}%;top:{y}%;'
        f'animation-delay:{d}s"></span>' for x, y, d in stars)
    return f'<div class="sky" aria-hidden="true">{"".join(ring)}{star_html}</div>'


def chips_row(chart, lang):
    """Quick-glance summary chips: chart ruler, sect, dominant element and
    modality, tightest aspect."""
    t, u = L[lang], UI[lang]
    herm = chart.get("hermetica", {})
    els = chart["balance"]["elements"]
    mods = chart["balance"]["modalities"]
    chips = []  # (label-HTML, value-text) — labels carry glossary tooltips
    ruler = herm.get("chart_ruler")
    if ruler and herm.get("chart_ruler_sign"):
        chips.append((tip(u["chip_ruler"], "wladca", lang),
                      f"{PLANET_GLYPH.get(ruler, '')} {t['planets'][ruler]} · "
                      f"{t['signs'][herm['chart_ruler_sign']]} "
                      f"({ROMAN[herm['chart_ruler_house'] - 1]})"))
    sect = chart["meta"]["sect"]
    chips.append((tip(t["labels"]["sect_l"], "sekta", lang),
                  t["labels"]["day_chart"] if sect == "day"
                  else t["labels"]["night_chart"]))
    dom_el = max(els, key=els.get)
    dom_mo = max(mods, key=mods.get)
    chips.append((tip(u["chip_elem"], "zywiol", lang),
                  f"{t['elements'][dom_el]} {els[dom_el]}/12"))
    chips.append((tip(u["chip_mode"], "jakosc", lang),
                  f"{t['modes'][dom_mo]} {mods[dom_mo]}/12"))
    asps = chart.get("aspects") or []
    if asps:
        a = asps[0]
        chips.append((tip(u["chip_tight"], "aspekt", lang),
                      f"{PLANET_GLYPH.get(a['a'], '')} "
                      f"{ASPECT_GLYPH[a['aspect']]} "
                      f"{PLANET_GLYPH.get(a['b'], '')} · {a['orb']:.1f}°"))
    body = "".join(f"<span class='chip'><b>{k}</b>{esc(v)}</span>"
                   for k, v in chips)
    return f"<div class='chips'>{body}</div>"


MONTHS = {
    "pl": ["styczeń", "luty", "marzec", "kwiecień", "maj", "czerwiec",
           "lipiec", "sierpień", "wrzesień", "październik", "listopad",
           "grudzień"],
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
}
TL_SPEED = {"Pluto": 0, "Neptune": 1, "Uranus": 2, "Saturn": 3, "Jupiter": 4,
            "Mars": 5, "Sun": 6, "Venus": 7, "Mercury": 8}


def transit_timeline(tr, lang, mark_date=None):
    """SVG timeline of transit windows: one bar per (body, aspect, natal
    point) window, brighter core where orb ≤ 1°, ◆ at exact hits, lunation
    markers on the bottom axis, dashed line at the reading date."""
    t, u = L[lang], UI[lang]
    d1 = dtm.date.fromisoformat(tr["meta"]["window"][0])
    d2 = dtm.date.fromisoformat(tr["meta"]["window"][1])
    span = max((d2 - d1).days, 1)
    X0, X1, W = 200, 1030, 1060

    def x(dstr):
        f = (dtm.date.fromisoformat(dstr[:10]) - d1).days / span
        return X0 + max(0.0, min(1.0, f)) * (X1 - X0)

    rows = sorted(tr["windows"],
                  key=lambda w: (TL_SPEED.get(w["body"], 9), w["start"]))
    RH, TOP = 30, 44
    H = TOP + len(rows) * RH + 64
    out = [f"<svg class='timeline' viewBox='0 0 {W} {H}' role='img' "
           f"aria-label='{esc(u['timeline'])}'>"]
    # month grid + labels
    m = dtm.date(d1.year, d1.month, 1)
    while m <= d2:
        if m >= d1:
            mx = x(m.isoformat())
            out.append(f"<line class='tl-grid' x1='{mx:.0f}' y1='{TOP - 16}' "
                       f"x2='{mx:.0f}' y2='{H - 40}'/>")
        lab = f"{MONTHS[lang][m.month - 1].capitalize()} {m.year}"
        out.append(f"<text class='tl-month' x='{x(m.isoformat()) + 6:.0f}' "
                   f"y='{TOP - 22}'>{lab}</text>")
        m = dtm.date(m.year + m.month // 12, m.month % 12 + 1, 1)
    out.append(f"<line class='tl-grid' x1='{X1}' y1='{TOP - 16}' "
               f"x2='{X1}' y2='{H - 40}'/>")
    # rows
    for i, w in enumerate(rows):
        y = TOP + i * RH
        cls = aspect_cls(w["angle"])
        bx1, bx2 = x(w["start"]), x(w["end"])
        if bx2 - bx1 < 6:
            bx2 = bx1 + 6
        out.append(f"<rect class='{cls}' x='{bx1:.0f}' y='{y + 9}' "
                   f"width='{bx2 - bx1:.0f}' height='11' rx='5.5' "
                   f"opacity='.32'/>")
        if w.get("tight_start"):
            tx1, tx2 = x(w["tight_start"]), x(w["tight_end"])
            if tx2 - tx1 < 5:
                tx2 = tx1 + 5
            out.append(f"<rect class='{cls}' x='{tx1:.0f}' y='{y + 9}' "
                       f"width='{tx2 - tx1:.0f}' height='11' rx='5.5' "
                       f"opacity='.9'/>")
        for ex in w.get("exact", []):
            exx = x(ex)
            out.append(f"<polygon class='tl-exact' points='{exx:.0f},"
                       f"{y + 8.5} {exx + 4.5:.0f},{y + 14.5} {exx:.0f},"
                       f"{y + 20.5} {exx - 4.5:.0f},{y + 14.5}'/>")
        name = t["planets"].get(w["natal"], w["natal"])
        rx = " Rx" if w.get("retro") else ""
        side = w.get("side", "")
        lab = (f"{PLANET_GLYPH.get(w['body'], '')}{rx} "
               f"{ASPECT_GLYPH[w['aspect']]} "
               f"{side}{PLANET_GLYPH.get(w['natal'], '')} {name} "
               f"· {w['min_orb']:.1f}°")
        out.append(f"<text class='glyph' x='8' y='{y + 19}'>{esc(lab)}</text>")
    # lunation axis
    ay = H - 40
    out.append(f"<line class='tl-axis' x1='{X0}' y1='{ay}' "
               f"x2='{X1}' y2='{ay}'/>")
    for lu in tr.get("lunations", []):
        lx = x(lu["date"])
        cls = "tl-new" if lu["type"] == "new_moon" else "tl-full"
        out.append(f"<circle class='{cls}' cx='{lx:.0f}' cy='{ay}' r='4.5'/>")
        d = dtm.date.fromisoformat(lu["date"])
        out.append(f"<text class='tl-date' x='{lx:.0f}' y='{ay + 18}' "
                   f"text-anchor='middle'>{d.day:02d}.{d.month:02d}</text>")
    # reading-date marker
    if mark_date:
        mx = x(mark_date)
        out.append(f"<line class='tl-mark' x1='{mx:.0f}' y1='{TOP - 16}' "
                   f"x2='{mx:.0f}' y2='{H - 40}'/>")
    out.append("</svg>")
    return "".join(out)


def ambient_html():
    """Side ornaments for wide screens: the Chaldean ladder of the seven
    planets (left) and a slowly counter-rotating astrolabe ring emerging
    from the right edge. Purely decorative, calm, non-interactive."""
    lad = "".join(
        f"<span class='lad' style='animation-delay:-{i * 1.7:.1f}s'>{g}</span>"
        for i, g in enumerate("♄♃♂☉♀☿☽"))  # Chaldean order: descent
    glyphs = []
    for i, g in enumerate(ZODIAC_GLYPHS):
        a = math.radians(i * 30 - 90)
        glyphs.append(f"<text x='{200 + 171 * math.cos(a):.0f}' "
                      f"y='{200 + 171 * math.sin(a):.0f}'>{g}</text>")
    ring = ("<svg class='amb-ring' viewBox='0 0 400 400'>"
            "<g class='amb-spin-a'>"
            "<circle cx='200' cy='200' r='192' stroke-width='.7' "
            "stroke-dasharray='3 7'/>"
            "<circle cx='200' cy='200' r='148' stroke-width='.5'/></g>"
            f"<g class='amb-spin-b'>{''.join(glyphs)}</g></svg>")
    stars = "".join(
        f"<span class='star' style='left:{x}%;top:{y}%;"
        f"animation-delay:{d}s'></span>"
        for x, y, d in ((30, 12, .5), (62, 27, 1.9), (44, 72, 3.0),
                        (70, 87, 1.1), (24, 46, 2.4)))
    return (f"<div class='amb-side amb-left' aria-hidden='true'>"
            f"<div class='ladder'>{lad}</div>{stars}</div>"
            f"<div class='amb-side amb-right' aria-hidden='true'>"
            f"{ring}{stars}</div>")


def topbar(lang, has_transits=False, links=None):
    u = UI[lang]
    if links is None:
        links = [("#kolo", u["nav_wheel"]), ("#tozsamosc", u["nav_tozs"]),
                 ("#domy", u["nav_houses"]), ("#sygnatura", u["nav_sig"])]
        if has_transits:
            links.append(("#tranzyty", u["nav_transits"]))
        links.append(("#reading", u["nav_read"]))
        links.append(("#mechanizm", u["nav_mech"]))
    nav = "".join(f"<a href='{h}'>{esc(n)}</a>" for h, n in links)
    return (f"<nav class='topbar' aria-label='{esc(u['nav_label'])}'>"
            f"<button class='orrery' id='totop' aria-label='{esc(u['totop'])}' "
            f"title='{esc(u['totop'])}'><span class='sun'></span>"
            f"<span class='orbit o1'><span class='pl'></span></span>"
            f"<span class='orbit o2'><span class='pl'></span></span></button>"
            f"<div class='navlinks'>{nav}</div>"
            f"<button class='themebtn' id='themebtn' "
            f"aria-label='{esc(u['theme_label'])}' "
            f"title='{esc(u['theme_label'])}'>☀</button>"
            f"<span class='progressbar' id='pbar' aria-hidden='true'></span>"
            f"</nav>")


def tipsheet(lang):
    u = UI[lang]
    return (f"<div class='tipsheet' id='tipsheet' role='dialog' "
            f"aria-label='{esc(u['def_label'])}'>"
            f"<div class='tiphead'><b id='tipterm'></b>"
            f"<button class='tipclose' aria-label='{esc(u['def_close'])}'>✕</button>"
            f"</div><p id='tipdef'></p></div>")


UI_JS = """
(function(){
  var d=document;
  var pb=d.getElementById('pbar');
  if(pb){addEventListener('scroll',function(){
    var h=d.documentElement,m=h.scrollHeight-h.clientHeight;
    pb.style.width=(m>0?h.scrollTop/m*100:0)+'%';},{passive:true});}
  var tt=d.getElementById('totop');
  if(tt){tt.addEventListener('click',function(){
    scrollTo({top:0,behavior:'smooth'});});}
  /* glossary bottom sheet — the readable tap target on touch screens */
  var sheet=d.getElementById('tipsheet');
  if(sheet){
    var term=d.getElementById('tipterm'),def=d.getElementById('tipdef');
    var close=function(){sheet.classList.remove('open');};
    d.addEventListener('click',function(e){
      var t=e.target.closest?e.target.closest('.tip'):null;
      if(t){term.textContent=t.textContent;
        def.textContent=t.getAttribute('data-tip')||'';
        sheet.classList.add('open');}
      else if(!sheet.contains(e.target)){close();}
    });
    d.addEventListener('keydown',function(e){if(e.key==='Escape')close();});
    sheet.querySelector('.tipclose').addEventListener('click',
      function(e){e.stopPropagation();close();});
  }
  /* gentle pointer parallax on the header sky */
  var sky=d.querySelector('.sky'),hd=d.querySelector('header.title');
  if(sky&&hd&&matchMedia('(prefers-reduced-motion: no-preference)').matches){
    hd.addEventListener('pointermove',function(e){
      var r=hd.getBoundingClientRect();
      var dx=(e.clientX-r.left)/r.width-.5,dy=(e.clientY-r.top)/r.height-.5;
      sky.style.transform='translate('+(dx*14).toFixed(1)+'px,'
        +(dy*10).toFixed(1)+'px)';});
    hd.addEventListener('pointerleave',function(){sky.style.transform='';});
  }
  /* light/dark theme toggle, persisted across visits */
  var tb=d.getElementById('themebtn');
  if(tb){
    var setIcon=function(){tb.textContent=
      d.documentElement.getAttribute('data-theme')==='light'?'☽':'☀';};
    setIcon();
    tb.addEventListener('click',function(){
      var el=d.documentElement;
      var next=el.getAttribute('data-theme')==='light'?'':'light';
      if(next){el.setAttribute('data-theme',next);}
      else{el.removeAttribute('data-theme');}
      try{if(next){localStorage.setItem('astro-theme',next);}
        else{localStorage.removeItem('astro-theme');}}catch(e){}
      setIcon();});
  }
  /* mobile accordion: h2-headed sections fold; anchors unfold their target */
  var mq=matchMedia('(max-width: 700px)');
  var secs=[].slice.call(d.querySelectorAll('main>section'));
  var open=function(s){s.classList.remove('closed');
    var h=s.querySelector('h2');
    if(h)h.setAttribute('aria-expanded','true');};
  secs.forEach(function(s){
    if(s.id==='mechanizm')return;
    var h=s.querySelector('h2');
    if(!h||h.parentNode!==s)return;
    s.classList.add('tog');
    h.setAttribute('tabindex','0');
    var tgl=function(){
      if(!d.body.classList.contains('acc'))return;
      s.classList.toggle('closed');
      h.setAttribute('aria-expanded',
        s.classList.contains('closed')?'false':'true');};
    h.addEventListener('click',tgl);
    h.addEventListener('keydown',function(e){
      if(e.key==='Enter'||e.key===' '){e.preventDefault();tgl();}});
  });
  var accApply=function(){
    if(mq.matches){d.body.classList.add('acc');
      secs.forEach(function(s){
        if(!s.classList.contains('tog'))return;
        s.classList.add('closed');
        s.querySelector('h2').setAttribute('aria-expanded','false');});}
    else{d.body.classList.remove('acc');
      secs.forEach(function(s){
        if(s.id==='mechanizm')return;
        s.classList.remove('closed');
        var h=s.querySelector('h2');
        if(h)h.removeAttribute('aria-expanded');});}
  };
  accApply();
  if(mq.addEventListener){mq.addEventListener('change',accApply);}
  else if(mq.addListener){mq.addListener(accApply);}
  /* the Mechanism annex folds on every viewport — the watch's case-back */
  var mech=d.getElementById('mechanizm');
  if(mech){
    var mh=mech.querySelector('h2');
    mh.setAttribute('tabindex','0');
    var mt=function(){mech.classList.toggle('closed');
      mh.setAttribute('aria-expanded',
        mech.classList.contains('closed')?'false':'true');};
    mh.addEventListener('click',mt);
    mh.addEventListener('keydown',function(e){
      if(e.key==='Enter'||e.key===' '){e.preventDefault();mt();}});
  }
  var openHash=function(id){var s=id&&d.getElementById(id);
    if(s&&(s.classList.contains('tog')||s.id==='mechanizm')){open(s);}};
  d.addEventListener('click',function(e){
    var a=e.target.closest?e.target.closest('a[href^="#"]'):null;
    if(a){openHash(a.getAttribute('href').slice(1));}});
  addEventListener('hashchange',function(){openHash(location.hash.slice(1));});
  if(location.hash){openHash(location.hash.slice(1));}
})();
"""


# ─────────────────────────────────────────────────────────────────────────────
# Assembly
# ─────────────────────────────────────────────────────────────────────────────


def build(chart, reading_text, lang, title, transits=None, mark_date=None):
    t, u = L[lang], UI[lang]
    meta = chart["meta"]
    prose, conf = extract_prose(reading_text) if reading_text else ([], [])
    prose_by_num = {}
    for ptitle, paras in prose:
        m = re.match(r"^(\d)", ptitle)
        if m:
            prose_by_num.setdefault(m.group(1), []).append((ptitle, paras))

    def sec_prose(n, titled=True):
        # sections whose data is rendered natively get prose without the
        # redundant "N · TITLE" heading
        return "".join(
            (f"<h3>{esc(pt)}</h3>" if titled else "") + prose_html(paras)
            for pt, paras in prose_by_num.get(n, []))

    hemi = "N" if meta["lat"] >= 0 else "S"
    hemi2 = "E" if meta["lon"] >= 0 else "W"
    tz = meta["tz"]
    tzs = f"UTC{'+' if tz >= 0 else '−'}{abs(tz):g}"
    metabox = (
        f"<div class='meta'>"
        f"<span><b>{esc(meta['name'])}</b> · {esc(meta['dob'])} {esc(meta['tob'])}</span>"
        f"<span>{abs(meta['lat']):.2f}°{hemi} {abs(meta['lon']):.2f}°{hemi2} · {tzs}</span>"
        f"<span>{esc(meta['zodiac'])} · {esc(meta['house_system_effective'])}</span>"
        f"<span>{esc(t['labels']['sect_l'])}: "
        f"{esc(t['labels']['day_chart'] if meta['sect'] == 'day' else t['labels']['night_chart'])}"
        f" · {esc(meta['ephemeris'])}</span></div>")

    conf_html = ""
    if conf:
        conf_html = (f"<h2>{esc(u['confidence'])}</h2><ul class='conf'>"
                     + "".join(f"<li>{esc(c)}</li>" for c in conf) + "</ul>")

    disclaimer = {
        "pl": "Ten odczyt jest hermetycznym zwierciadłem do refleksji i samopoznania — "
              "mapą tendencji i czasu, nie przepowiednią ustalonych zdarzeń. Astrologia "
              "jest tradycją symboliczną i nie zastępuje profesjonalnej porady medycznej, "
              "prawnej, psychologicznej ani finansowej. „Jak na górze, tak na dole; "
              "poznaj samego siebie.”",
        "en": "This reading is a Hermetic mirror for reflection and self-knowledge — a "
              "map of tendencies and timing, not a prediction of fixed events. Astrology "
              "is a symbolic tradition, not a substitute for professional medical, legal, "
              "psychological, or financial advice. “As above, so below; know thyself.”",
    }[lang]

    # transit/period readings carry no 2/5/6 prose — skip empty sections and
    # their nav links instead of rendering bare headings
    tozs = sec_prose('2', titled=False)
    domy = sec_prose('5', titled=False)
    tozs_sec = (f"<section id=\"tozsamosc\"><h2>{esc(u['nav_tozs'])}</h2>"
                f"{tozs}</section>") if tozs else ""
    domy_sec = (f"<section id=\"domy\"><h2>{esc(u['nav_houses'])}</h2>"
                f"{domy}</section>") if domy else ""
    nav_links = [("#kolo", u["nav_wheel"])]
    if tozs:
        nav_links.append(("#tozsamosc", u["nav_tozs"]))
    if domy:
        nav_links.append(("#domy", u["nav_houses"]))
    nav_links.append(("#sygnatura", u["nav_sig"]))
    if transits:
        nav_links.append(("#tranzyty", u["nav_transits"]))
    nav_links += [("#reading", u["nav_read"]), ("#mechanizm", u["nav_mech"])]

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<script>try{{var _t=localStorage.getItem('astro-theme');
if(_t)document.documentElement.setAttribute('data-theme',_t);}}catch(e){{}}</script>
<style>{CSS}</style>
</head>
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
{metabox}
{chips_row(chart, lang)}
<section id="kolo" aria-label="{esc(u['wheel_desc'])}">
  <div class="wheelwrap">{wheel_svg(chart, lang)}
    <div>{balance_bars(chart, lang)}</div></div>
</section>
{tozs_sec}
{domy_sec}
<section id="sygnatura"><h2>{esc(u['signature'])}</h2>{signature_panel(chart, lang)}
{sec_prose('6', titled=False)}</section>
{(f"<section id='tranzyty'><h2>{esc(u['timeline'])}</h2>"
  f"{scrollx(transit_timeline(transits, lang, mark_date), u['timeline'])}"
  f"<p class='tl-legend'>{esc(u['tl_legend'])}</p></section>") if transits else ""}
<section class="reading" id="reading"><h2>{esc(u['reading'])}</h2>
{sec_prose('7')}{sec_prose('8')}{conf_html}</section>
<section id="mechanizm" class="closed">
<h2 aria-expanded="false">{esc(u['mech_title'])}</h2>
<p class="mech-hint">{esc(u['mech_hint'])}</p>
{sec_prose('1', titled=False)}
<h3 class="mech-h3">{esc(u['positions'])}</h3>{scrollx(positions_table(chart, lang), u['positions'])}
<h3 class="mech-h3">{esc(u['dignity'])}</h3>{scrollx(dignity_table(chart, lang), u['dignity'])}
{sec_prose('3', titled=False)}
<h3 class="mech-h3">{esc(UI[lang]['aspect_grid'])}</h3>{scrollx(aspect_grid(chart, lang), u['aspect_grid'])}
{scrollx(aspect_list(chart, lang), u['aspect_list'])}{sec_prose('4', titled=False)}
</section>
<footer><p>{esc(u['tiphint'])}</p><p>{esc(disclaimer)}</p><p>{esc(u['generated'])}</p></footer>
</main>
{tipsheet(lang)}
<script>{UI_JS}</script>
</body>
</html>"""


def main():
    p = argparse.ArgumentParser(description="Export chart.json (+reading.md) to HTML")
    p.add_argument("chart_json")
    p.add_argument("--reading", help="reading.md to embed as interpretation")
    p.add_argument("--transits", help="transits.json (from transits.py) — "
                   "adds the transit-timeline section")
    p.add_argument("--mark-date", help="YYYY-MM-DD to mark on the timeline "
                   "(typically the reading date)")
    p.add_argument("--lang", default="pl", choices=["en", "pl"])
    p.add_argument("--out", required=True)
    p.add_argument("--title", default=None)
    args = p.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    chart = json.load(open(args.chart_json, encoding="utf-8"))
    if "error" in chart:
        print(json.dumps(chart))
        sys.exit(1)
    reading = (open(args.reading, encoding="utf-8").read()
               if args.reading else "")
    transits = (json.load(open(args.transits, encoding="utf-8"))
                if args.transits else None)
    title = args.title or {
        "pl": f"Horoskop — {chart['meta']['name']}",
        "en": f"Chart — {chart['meta']['name']}",
    }[args.lang]
    html_text = build(chart, reading, args.lang, title,
                      transits=transits, mark_date=args.mark_date)
    open(args.out, "w", encoding="utf-8", newline="\n").write(html_text)
    print(f"written {args.out} ({len(html_text)} bytes)")


if __name__ == "__main__":
    main()
