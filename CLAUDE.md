# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

**Astrologia** hosts a single Claude skill: **`hermetic-astrology`** — a Western/European
**tropical** astrology engine built on the classical/Hermetic tradition. It casts and
interprets natal charts, transits, synastry, solar returns, and electional (planetary-hour)
timing, and saves each reading to a structured `output/` tree.

It was adapted from the Vedic Jyotish skill at
`github.com/deepanshutomar/Vedic-Astrology-Skill-` — the *architecture* (SKILL.md
orchestrator + lazy-loaded resources + optional Python compute engine + output template +
dual execution mode) was kept; the *content and engine were rebuilt* for the European
tradition. Key differences from the Vedic source:
- **Tropical zodiac, no ayanamsa** (measured from the vernal equinox, not fixed stars).
- **Aspect-based** interpretation (Ptolemaic angles) rather than Vedic house-aspects.
- **Essential dignity + sect** for planetary strength rather than the Vedic strength/dasha system.
- A **Hermetic layer**: "as above, so below", the seven principles, decans/faces, and
  planetary hours.
- The engine uses **Skyfield + JPL de421 (geocentric, tropical)**, fixing the reference
  engine's bugs (heliocentric longitudes, broken node/retrograde logic, hand-rolled ascendant).
  Skyfield was chosen over `pyswisseph` because pyswisseph ships no binary wheels in this
  environment and needs a C++ compiler; Skyfield is pure-Python and installs from wheels.
  Angles (ASC/MC) and house cusps are computed in-engine; planet positions come from Skyfield.

## Layout

```
CLAUDE.md
output/                     ← generated readings (see "Output convention")
  README.md
.claude/skills/hermetic-astrology/
  SKILL.md                  ← orchestrator: frontmatter (triggers) + 9-step pipeline
  compute/chart_engine.py   ← Skyfield/de421 chart engine (Compute Mode); caches de421.bsp here
  resources/                ← lazy-loaded knowledge base (one file per domain)
  templates/full-reading.md ← final report skeleton
  requirements.txt · install.sh
```

The **skill itself contains no glue code** — `SKILL.md` is a set of natural-language
instructions Claude follows. To understand behavior, read `SKILL.md` first; it names which
`resources/*.md` file backs each step (the "Resource Index" table at the bottom).

## Commands

Compute Mode is optional; the skill falls back to Prompt Mode (Claude does the math) when
Python/`skyfield` is absent. On Windows here use the **`py -3.13`** launcher — plain `python`
is the Microsoft Store stub, and Python 3.14 has no `skyfield`-friendly build (numpy wheel gaps).

```bash
# Install compute dependencies (one-time)
py -3.13 -m pip install -r .claude/skills/hermetic-astrology/requirements.txt
#   or: bash .claude/skills/hermetic-astrology/install.sh

# Run the engine directly (prints a JSON chart; first run downloads de421.bsp ~17 MB)
py -3.13 .claude/skills/hermetic-astrology/compute/chart_engine.py \
  --dob 1993-06-14 --tob 15:40 --lat 54.35 --lon 18.65 --tz 2 --house-system W

# Smoke-test
py -3.13 .claude/skills/hermetic-astrology/compute/chart_engine.py --dob 2000-01-01 --lat 0 --lon 0 --tz 0

# Render a computed chart as finished report tables (Polish or English)
py -3.13 .claude/skills/hermetic-astrology/compute/render_chart.py path/to/chart.json --lang pl

# Export an accessible HTML report (SVG wheel + tables + reading prose + tooltips)
py -3.13 .claude/skills/hermetic-astrology/compute/render_html.py chart.json \
  --reading reading.md --lang pl --out reading.html

# Natal transit windows (slow planets + lunations) — feeds the HTML timeline
py -3.13 .../compute/transits.py chart.json --from 2026-08-01 --to 2026-09-30 \
  > transits.json   # then: render_html.py ... --transits transits.json --mark-date <reading-date>

# Relationship tools: synastry, midpoint composite, relationship transits
py -3.13 .../compute/synastry.py chartA.json chartB.json --nameA "..." --nameB "..."
py -3.13 .../compute/composite.py chartA.json chartB.json
py -3.13 .../compute/synastry_transits.py chartA chartB synastry.json composite.json \
  --from 2026-08-01 --to 2026-09-30
py -3.13 .../compute/render_html_synastry.py chartA chartB synastry.json \
  --composite composite.json --reading reading.md --lang pl --out reading.html

# PDF — ONLY when the user explicitly asks (user rule), via headless Edge:
"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new \
  --disable-gpu --print-to-pdf="reading.pdf" --no-pdf-header-footer "file:///…/reading.html"
```

**Renderer changes do NOT retro-apply (user rule): after editing render code, never
mass-regenerate existing `output/` HTML — regenerate only the reading(s) the user names.**
The UI v2 layer (sticky topbar nav + orrery animation, header zodiac-ring sky, tap-friendly
glossary bottom sheet, summary chips, dignity mini-bars, aspect-grid heat map, degree
dials in the positions table, mobile section accordion, light/dark theme toggle persisted
in localStorage, transit-timeline SVG via `transits.py` + `--transits`/`--mark-date`) ships
in `render_html.py`; it is applied only to selected pilot readings in `output/`
(never mass-regenerate the rest). Polish terminology (2026-08-08 audit): „Peregryn”
(not Peregrin), „Termy” (not Term), „Losy” for Lots (not „Loty”), Mercury sect status
„neutralny” — fixed in `render_chart.py` L and the `render_html.py` GLOSS; future
readings inherit them automatically.

**Standard deliverables per reading: `reading.md` + `reading.html` (+ raw JSONs). PDF only
on explicit request — per reading, in the current conversation.** That other folders contain
PDFs does NOT imply a new reading should get one; do not generate PDFs "for consistency" or
when resuming interrupted work. Same for named share copies (`<Znak>_<rok>_….html/pdf`). Readings are written in Polish (user preference) and must be
self-contained per person — never reference other subjects' readings; quoting the same
person's earlier readings is fine.

Engine args: `--name --dob YYYY-MM-DD --tob HH:MM --lat(+N) --lon(+E) --tz(UTC offset)
--house-system` (`W` Whole Sign default, `E` Equal, `O` Porphyry, `P` Placidus). Latitude is
+North, longitude is **+East**, tz is the UTC offset (e.g. `-5` for New York EST; mind
historical DST at the birth date). On a missing dependency the
engine prints `{"error": ...}` and exits 1 — the signal to use Prompt Mode.

> **Environment note:** `python`/`python3` on PATH is the Windows Store stub. A real
> **Python 3.13.14** is installed (`py -3.13`) with `skyfield` — Compute Mode works and is
> verified. `pyswisseph` is NOT usable here (no wheels + no C++ compiler); do not depend on it.
> `py -3.14` exists but lacks the needed wheels. Console is cp1250, so the engine forces UTF-8
> on stdout for the zodiac glyphs.

## Architecture notes (the big picture)

- **Two execution modes** (`SKILL.md` → EXECUTION MODES). Compute Mode runs the engine and
  parses JSON; Prompt Mode approximates positions from rules embedded in `SKILL.md` and the
  resources. Interpretation logic is identical; only raw precision differs.
- **The engine is pure computation, no interpretation.** `chart_engine.py` emits one JSON
  object: `planets` (sign/house/dignities/dignity_score/sect_status/solar_condition/
  retrograde/speed/faces), `angles` (ASC/MC + rulers), `lots` (⊕ Fortune, ⊗ Spirit,
  sect-aware), `aspects` (Ptolemaic + minor, orb & applying/separating from the true orb
  derivative, +2° luminary bonus on majors, aspects to ASC/MC with phase `—`), `balance`,
  and `hermetica` (sect from the Sun's true altitude, planetary day/hour with
  sunrise-to-sunrise days, chart ruler). All interpretation lives in `SKILL.md` + resources.
- **`compute/render_chart.py` renders chart.json into the finished 72-column report
  tables** (box-drawing chart table, dignity table, aspect grid + list, balance bars,
  hermetic panel) in English or Polish (`--lang pl`). Use it instead of hand-aligning
  tables; the reading template embeds its output directly.
- **Relationship pipeline:** `synastry.py` (inter-aspects/overlays/fit) →
  `composite.py` (shorter-arc midpoint chart, chart-shaped JSON so the SVG wheel works
  on it) → `synastry_transits.py` (transits to the composite, "string activations" of
  tight inter-aspects, lunations in composite houses). Reference: `resources/composite.md`.
- **`render_html.py` embeds a PL/EN lay glossary (GLOSS)** — hover/focus tooltips on
  technical terms (Sekta, Dekany, Loty, Węzły, dignity names, Orb, Faza…). When adding
  new UI vocabulary, add a GLOSS entry and wrap the label with `tip()`.
- **Static data tables live in the engine** (`chart_engine.py` top): domiciles, exaltations,
  Egyptian TERMS, Chaldean FACE_CYCLE, TRIPLICITY, ASPECTS, DAY_RULER. The same tables are
  duplicated in prose in `resources/dignities.md` / `decans.md` for Prompt Mode — **keep
  these two in sync when editing either.**
- **Sect drives dignity.** The engine computes day/night from the Sun's true altitude
  (house-system independent), selects the day-or-night triplicity ruler (Lilly's scheme —
  Water = Mars/Mars, unlike Dorothean), and reports each classical planet's `sect_status`.
  Dignity scoring follows Lilly (domicile +5, exalt +4, triplicity +3, term +2, face +1;
  detriment −5, fall −4, peregrine −5 — **peregrine stacks with detriment/fall** when the
  planet holds no dignity at all, e.g. Sun in Libra = Fall + Peregrine = −9).
- **Interpretive weighting** (`SKILL.md` → SYNTHESIS): chart ruler & luminaries > tight
  applying aspects & angular planets > essential dignity & sect > house emphasis > minor
  aspects/decans.

## Output convention (important)

Individual readings (one folder per person, so different people never collide):
```
output/<zodiak>_<dob>/<dob>_<reading-date>_<method>_<purpose>/reading.md
```
`<zodiak>` = Polish Sun-sign name, lowercase ASCII (waga, wodnik, baran…); dates
`YYYY-MM-DD`; purpose in Polish kebab-case (ogolny, kariera…). Synastry lives in its own
tree: `output/synastria/<zodA>_<dobA>_x_<zodB>_<dobB>_<reading-date>_<purpose>/`.
Each folder holds `reading.md` + `reading.html` + `reading.pdf` + `chart.json`
(`synastry.json` for synastry). Full spec in `output/README.md` and `SKILL.md` Step 9.

## Export / distribution

The project is export-ready; `.gitignore` defines the boundary. When asked to package or
publish, produce `export/Astrologia_hermetic-astrology_<date>.zip` mirroring the repo tree
but **excluding**: `output/` except `output/README.md` (readings hold private birth data of
real people — never export them), `compute/de421.bsp` (auto-downloaded on first run),
`__pycache__/`, `.claude/settings.local.json`, and `export/` itself. Stage in the scratchpad
(robocopy `/XD __pycache__ /XF de421.bsp`; robocopy exit code 1 = success) and
`Compress-Archive`.

## Interpretive & ethical constraints (baked into the skill)

These are enforced in `SKILL.md` and `resources/hermetic-principles.md` — preserve them in
any edit: probabilistic, non-fatalistic language ("tendency/invitation", never "you will");
no fear-based, deterministic, or medical/legal/financial-prescriptive claims; time windows
as ranges; the chart framed as a mirror for self-knowledge. Never refuse for missing birth
data — default (noon / capital city) and flag the confidence.

## Conventions when editing

- **Astronomy uses Skyfield + JPL de421.** Planet positions are geocentric apparent ecliptic
  longitudes of date (`ecliptic_latlon(epoch=t)` = tropical). de421 covers 1900–2049 (the
  engine validates this) and is cached as `compute/de421.bsp`. Outer planets use their
  `... barycenter` keys; **Chiron is not in de421 and is intentionally omitted**. Lunar nodes
  are the *mean* node (Meeus polynomial, with its speed ~−0.053°/day). Angles use apparent
  sidereal time (`t.gast`) + true obliquity; houses are computed in-engine (`house_cusps`
  returns the cusps AND the effective system name — Placidus falls back to Porphyry near the
  poles). Speeds are centered differences (±0.02 d). The engine honors a strict error
  contract: `{"error": ...}` + exit 1 on every failure, including argparse errors. Cast
  numpy scalars to `float`/`bool` before `json.dumps`.
- **Modern planets (Uranus/Neptune/Pluto) receive no dignity/rulership** in scoring — that is
  intentional traditional practice; they are read as generational overlays only.
- When adding a technique, add a block under `SKILL.md` Step 7 and, if it needs data, a new
  `resources/*.md` file plus a row in the Resource Index table.
