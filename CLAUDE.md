# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

**Astrologia** hosts a single Claude skill: **`hermetic-astrology`** — a Western/European
**tropical** astrology engine built on the classical/Hermetic tradition. It casts and
interprets natal charts, transits, synastry, solar returns, and electional (planetary-hour)
timing, and saves each reading to a structured `output/` tree.

Standard skill architecture: `SKILL.md` orchestrator + lazy-loaded `resources/` + optional
Python compute engine + output template + dual execution mode. Foundations: tropical zodiac
(no ayanamsa), Ptolemaic aspects, essential dignity + sect for planetary strength, and a
Hermetic layer (seven principles, decans/faces, lots, planetary hours).

## Layout

```
CLAUDE.md
output/                     ← generated readings (see "Output convention")
.claude/skills/hermetic-astrology/
  SKILL.md                  ← orchestrator: frontmatter (triggers) + 9-step pipeline
  compute/                  ← engine + renderers (pure Python); caches de421.bsp here
  resources/                ← lazy-loaded knowledge base (one file per domain)
  templates/full-reading.md ← final report skeleton
  requirements.txt · install.sh
```

The **skill contains no glue code** — `SKILL.md` is natural-language instructions Claude
follows. To understand behavior, read `SKILL.md` first; its Resource Index maps each step
to its backing `resources/*.md` file. **Canonical run commands live in `SKILL.md`**
(Step 1 engine, Step 7 method tools, Step 9 renderers + PDF) — they are not duplicated here.

## Environment & running

- Interpreter: **`py -3.13`** (has `skyfield`; Compute Mode verified). Plain `python` is
  the Microsoft Store stub; `py -3.14` lacks the needed wheels. `pyswisseph` is NOT usable
  here (no wheels, no C++ compiler) — the engine uses **Skyfield + JPL de421**, pure Python.
  Console is cp1250, so the engine forces UTF-8 on stdout for the glyphs.
- One-time install: `py -3.13 -m pip install -r .claude/skills/hermetic-astrology/requirements.txt`
  (or `install.sh`). The first engine run downloads `de421.bsp` (~17 MB) into `compute/`.
- Smoke-test:
  `py -3.13 .claude/skills/hermetic-astrology/compute/chart_engine.py --dob 2000-01-01 --lat 0 --lon 0 --tz 0`
- Engine args: `--name --dob YYYY-MM-DD --tob HH:MM --lat(+N) --lon(+E) --tz(UTC offset;
  mind historical DST) --house-system` (`W` Whole Sign default, `E` Equal, `O` Porphyry,
  `P` Placidus). On EVERY failure the engine prints `{"error": ...}` and exits 1 — the
  signal to fall back to Prompt Mode.

## Binding user rules

- **Renderer changes do NOT retro-apply:** after editing render code, never mass-regenerate
  existing `output/` HTML — regenerate only the reading(s) the user names. The UI-v2 shell
  in `render_html.py` is applied only to selected pilot readings.
- **Standard deliverables per reading: `reading.md` + `reading.html` (+ raw JSONs). PDF and
  named share copies (`<Znak>_<rok>_….html/pdf`) ONLY on explicit request — per reading, in
  the current conversation.** That other folders contain PDFs does NOT imply a new reading
  gets one; never generate them "for consistency" or when resuming interrupted work.
- Readings are written in **Polish** and are **self-contained per person** — never reference
  other subjects' readings; quoting the same person's earlier readings is fine.

## Architecture notes

- **Two execution modes** (`SKILL.md` → EXECUTION MODES): Compute Mode runs the engine and
  parses JSON; Prompt Mode approximates positions from rules in `SKILL.md` + resources.
  Interpretation logic is identical; only raw precision differs.
- **The engine is pure computation, no interpretation.** One JSON object — `planets`
  (dignities, score, sect_status, solar_condition, retrograde, faces), `angles`, `lots`,
  `aspects` (orb + applying/separating, +2° luminary bonus on majors, aspects to ASC/MC),
  `balance`, `hermetica` (sect, planetary day/hour, chart ruler). All interpretation lives
  in `SKILL.md` + resources. `render_chart.py` turns chart.json into the finished 72-column
  report tables (en/pl) — never hand-align tables.
- **Relationship pipeline:** `synastry.py` (inter-aspects/overlays/fit) → `composite.py`
  (shorter-arc midpoint chart, chart-shaped JSON so the SVG wheel works on it) →
  `synastry_transits.py` (transits to composite, "string activations", lunations).
  Reference: `resources/composite.md`.
- **`render_html.py` embeds a PL/EN lay glossary (GLOSS)** — when adding UI vocabulary,
  add a GLOSS entry and wrap the label with `tip()`.
- **Static data tables live in `chart_engine.py`** (domiciles, exaltations, Egyptian TERMS,
  Chaldean FACE_CYCLE, TRIPLICITY, ASPECTS, DAY_RULER); the same tables are duplicated in
  prose in `resources/dignities.md` / `decans.md` for Prompt Mode — **keep the two in sync.**
- **Sect & dignity — deliberate choices:** sect from the Sun's true altitude (house-system
  independent); Lilly's triplicity scheme (Water = Mars/Mars, unlike Dorothean); Lilly
  scoring where **peregrine (−5) stacks with detriment/fall** when the planet holds no
  dignity at all (e.g. Sun in Libra = Fall + Peregrine = −9).
- **Modern planets (Uranus/Neptune/Pluto) receive no dignity/rulership** — intentional
  traditional practice; read as generational overlays only.

## Output convention (important)

```
output/<zodiak>_<dob>/<dob>_<reading-date>_<method>_<purpose>/   # one folder per person
output/synastria/<zodA>_<dobA>_x_<zodB>_<dobB>_<reading-date>_<purpose>/
```

`<zodiak>` = Polish Sun-sign name, lowercase ASCII (waga, wodnik…); dates `YYYY-MM-DD`;
purpose in Polish kebab-case (ogolny, kariera…). Full spec: `output/README.md` and
`SKILL.md` Step 9.

## Export / distribution

`.gitignore` defines the boundary. On request, build
`export/Astrologia_hermetic-astrology_<date>.zip` mirroring the repo but **excluding**:
`output/` except `output/README.md` (readings hold private birth data of real people —
never export them), `compute/de421.bsp`, `__pycache__/`, `.claude/settings.local.json`,
`export/`. Stage in the scratchpad (robocopy `/XD __pycache__ /XF de421.bsp`; robocopy
exit code 1 = success), then `Compress-Archive`.

## Interpretive & ethical constraints (baked into the skill)

Enforced in `SKILL.md` and `resources/hermetic-principles.md` — preserve in any edit:
probabilistic, non-fatalistic language ("tendency/invitation", never "you will"); no
fear-based, deterministic, or medical/legal/financial-prescriptive claims; time windows as
ranges; the chart as a mirror for self-knowledge. Never refuse for missing birth data —
default (noon / capital city) and flag the confidence.

## Conventions when editing

- **Astronomy:** geocentric apparent ecliptic longitudes of date (`ecliptic_latlon(epoch=t)`
  = tropical); de421 covers 1900–2049 (engine-validated). Outer planets use `... barycenter`
  keys; **Chiron is not in de421 — intentionally omitted.** Nodes are the *mean* node
  (Meeus polynomial). Angles use apparent sidereal time (`t.gast`) + true obliquity;
  `house_cusps` returns the cusps AND the effective system name (Placidus falls back to
  Porphyry near the poles). Speeds are centered differences (±0.02 d). Strict error
  contract: `{"error": ...}` + exit 1 on every failure, including argparse. Cast numpy
  scalars to `float`/`bool` before `json.dumps`.
- When adding a technique: a block under `SKILL.md` Step 7 plus, if it needs data, a new
  `resources/*.md` file and a row in the Resource Index table.
