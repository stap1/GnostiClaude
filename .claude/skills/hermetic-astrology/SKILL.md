---
name: hermetic-astrology
description: >
  Western/European tropical astrology with a Hermetic foundation. Casts and interprets
  natal birth charts, transits, synastry (compatibility), solar returns, and electional
  timing (planetary hours). Triggers when the user gives a name and/or birth date (with or
  without time and place) and asks for a birth chart, natal reading, horoscope, star chart,
  "what's my rising/Sun/Moon sign", planetary positions, aspects, essential dignities,
  compatibility between two people, a year-ahead / solar-return reading, current transits,
  or a good time (planetary hour) to do something. Also triggers on "read my chart",
  "cast my horoscope", "astrology reading", "natal chart", "zodiac reading". Uses the
  tropical zodiac and classical/Hermetic technique (essential dignities, Ptolemaic aspects,
  Egyptian terms, Chaldean faces/decans, chart sect, planetary hours). Always proceed even
  if birth time or place is approximate or missing — flag the uncertainty and continue.
---

# Hermetic Astrology — Western Tropical Chart Engine

A traditional/Hermetic Western astrology engine. It casts a geocentric **tropical** chart
and interprets it through the classical apparatus — essential dignities, Ptolemaic aspects,
terms, faces, sect, and planetary hours — framed by the Hermetic principle *"as above, so
below"* (see `resources/hermetic-principles.md`). It is derived structurally from a Vedic
Jyotish skill but rebuilt for the European tradition: **tropical zodiac (no ayanamsa),
aspect-based (not house-aspect), and dignity-based strength.**

## EXECUTION MODES

| Mode | Condition | How it works |
|------|-----------|--------------|
| **Compute Mode** | Python + `skyfield` available | Run `compute/chart_engine.py`, parse the JSON, then interpret. |
| **Prompt Mode** | No Python / no skyfield | Calculate approximate positions from the rules below, then interpret. |

**Auto-detect:** try Compute Mode first. If Python or `skyfield` is missing (the script
prints `{"error": ...}` and exits 1 — it does so on EVERY failure, including bad arguments),
silently switch to Prompt Mode — do not burden the user with the failure. Interpretation
quality should be comparable; only the raw positions are less precise. On Windows here, the
working interpreter is `py -3.13`; plain `python` may be the Store stub. The first Compute
run downloads `de421.bsp` (~17 MB) into `compute/`.

---

## WELCOME MENU (bare invocation)

When the skill is invoked WITHOUT a concrete task ("astrologia", "co potrafisz",
the skill name alone), greet in the user's language with one short line and a
numbered menu — then wait for the choice:

```
Astrologia hermetyczna — co przygotować?

1 · Tranzyty na dzień  — „1” lub „tranzyty [data]” → pogoda dnia dla Twojej
    karty (domyślnie: dziś)
2 · Natal              — pełny horoskop urodzeniowy (data, godzina, miejsce)
3 · Tranzyty na okres  — prognoza z kalendarium i osią czasu
4 · Synastria          — dopasowanie dwojga + karta kompozytowa
5 · Tranzyty relacji   — kalendarz pary na wybrane okno
6 · Rewolucja słoneczna — tematy roku od urodzin do urodzin
7 · Elekcja terminu    — dobry dzień i godzina planetarna na przedsięwzięcie
```

**Shortcut „tranzyty na dzień” (option 1):** `tranzyty`, `tranzyty jutro`,
`tranzyty 15.09` → a compact one-day snapshot for THE QUERENT'S chart: cast the
sky for that date, list exact/tight aspects to the querent's natal points (fast
planets included), the Moon's sign + natal house, the planetary day & hour
rulers, and a short "pogoda dnia" paragraph (no full report skeleton; save as
`…_transits_dzien-<data>/` per the output convention only if the user wants it
kept, otherwise answer inline).

**The querent's chart:** use the natal chart the user has designated as their
own (an existing `output/<...>/chart.json` or session memory). If none is
known, ask ONCE for birth data and offer to remember the folder as "karta
pytającego". NEVER hard-code anyone's birth data in this file, README, or any
committed file — the repository is public; real charts live only in `output/`
(git-ignored).

---

## STEP 0 — INTAKE

Collect and normalize:

| Field | Notes |
|-------|-------|
| **Name / label** | Optional; default "Querent". |
| **Date of birth** | Any readable format → normalize to `YYYY-MM-DD`. **Required.** |
| **Time of birth** | `HH:MM` 24h. If missing → use `12:00` and flag Ascendant/houses as low-confidence. |
| **Place of birth** | City → geocode to latitude/longitude and UTC offset. |
| **Reading type ("method")** | natal (default), transits, synastry, solar-return, electional. |
| **Purpose** | Why they're asking (self, career, relationship, year-ahead, timing…). Default "general". |

**Rules**
- Never refuse for missing data — default and proceed with a clear caveat.
- No birth time → state: *"Birth time not given; using noon. The Ascendant, Midheaven,
  house placements, and the Moon's exact degree may be off — treat those as provisional."*
- Vague time ("morning", "around 5") → proceed, flag as medium/low confidence.
- Only a country → use the capital, flag it.

**Geocoding (Prompt Mode)** — use known coordinates (lat +N/−S, lon +E/−W, and UTC offset):
Warsaw 52.23, 21.01, +1/+2 · London 51.51, −0.13, 0/+1 · Berlin 52.52, 13.40, +1/+2 ·
Paris 48.86, 2.35, +1/+2 · Rome 41.90, 12.50, +1/+2 · New York 40.71, −74.01, −5/−4 ·
Los Angeles 34.05, −118.24, −8/−7. For others, use the nearest major city and flag it.
Account for daylight-saving time at the birth date when known.

---

## STEP 1 — CAST THE CHART

### Compute Mode
```bash
py -3.13 compute/chart_engine.py \
  --name "Name" --dob "YYYY-MM-DD" --tob "HH:MM" \
  --lat 54.35 --lon 18.65 --tz 2 --house-system W
```
`--house-system`: `W` Whole Sign (default, best for uncertain times), `E` Equal,
`O` Porphyry, `P` Placidus (falls back to Porphyry near the poles — the applied system is
in `meta.house_system_effective`). Parse the JSON; every later step draws from it
(`planets`, `angles`, `lots`, `aspects`, `balance`, `hermetica`). `--lat` is +North,
`--lon` is +East, `--tz` is the UTC offset (mind historical DST). Save the JSON as
`chart.json`, then render the report tables with:

```bash
py -3.13 compute/render_chart.py path/to/chart.json --lang pl   # or en
```

The renderer emits the finished 72-column tables (chart, dignities, aspect grid & list,
balance bars, hermetic panel) — paste them into the template and write only the prose.

### Prompt Mode (approximation)
- **Tropical positions — no ayanamsa.** Estimate the Sun's sign/degree from the date
  (Sun ≈ 0° of the current sign at each ingress; ~1°/day). Estimate the Moon (~13°/day,
  ~2.5 days/sign) and the visible planets from ephemeris knowledge for the year.
- **Ascendant** ≈ from birth time + latitude (rises ~1 sign / 2 hours; the Sun's sign is
  rising near sunrise). Flag as approximate.
- **Houses:** use **Whole Sign** in Prompt Mode (Ascendant's sign = 1st house, and so on) —
  it is the most robust without exact time.
- Compute **aspects** by comparing longitudes to the angles in `resources/aspects.md`.

**Output — the chart table:**
```
NATAL CHART — Tropical / [House System]
Planet      | Sign          | Deg     | House | Dignity        | Motion
------------+---------------+---------+-------+----------------+--------
Ascendant   | [Sign]        | [d°m']  |  1    | —              | —
Sun         | [Sign]        | [d°m']  | [H]   | [dignities]    | —
Moon        | [Sign]        | [d°m']  | [H]   | [dignities]    | —
Mercury …   | …             | …       | …     | …              | R?
...
Midheaven   | [Sign]        | [d°m']  | 10    | —              | —
```
→ Reference: `resources/planets.md`, `resources/signs.md`, `resources/houses.md`.

---

## STEP 2 — CORE IDENTITY: THE "BIG THREE" + CHART RULER

Synthesize the four keystones (3–5 sentences, personality only — no prediction yet):
- **Sun** (sign, house) — vital purpose, the conscious Self, "what lights you."
- **Moon** (sign, house) — emotional nature, instinct, needs, "what soothes you."
- **Ascendant** (sign + its ruler = the **chart ruler**) — temperament, body, the way
  you meet the world. Note where the chart ruler sits (its sign & house) — it "steers"
  the whole nativity.
Reference: `resources/planets.md`, `resources/signs.md`.

---

## STEP 3 — ESSENTIAL DIGNITY & SECT (planetary strength)

Determine **chart sect** first — day chart if the Sun is above the horizon. Compute Mode
derives this from the Sun's true altitude (`meta.sect`, `hermetica.sun_altitude_deg`);
in Prompt Mode estimate from birth time vs. sunrise/sunset. Then, for each of the seven
classical planets, read its dignities and condition (Compute Mode supplies `dignities`,
`dignity_score`, `sect_status` (of sect / contrary / common), and `solar_condition`
(cazimi / combust / under beams / free); in Prompt Mode derive them from
`resources/dignities.md` and `resources/planets.md`):

```
DIGNITY & CONDITION
Planet   | Sign      | Dignities                | Score | Sect status
---------+-----------+--------------------------+-------+-------------
Sun      | Leo       | Domicile, Triplicity     |  +8   | of sect (day)
Mars     | Cancer    | Fall                     |  −4   | contrary
...
```
Temper each essential score with **accidental** condition — house angularity, retrograde,
combustion, aspects from benefics/malefics. Reference: `resources/dignities.md`,
`resources/planets.md` (sect).

---

## STEP 4 — ASPECTS

List the significant aspects (Compute Mode: `aspects`, sorted by orb). Prioritize:
1. Aspects to the **Sun, Moon, Ascendant, MC, and chart ruler**.
2. **Tight, applying** aspects over wide, separating ones.
3. Note any **configurations** (stellium, T-square, grand trine, yod…).
Interpret each in light of the two planets' **condition and sect** — a hard aspect between
dignified planets can be productive. Reference: `resources/aspects.md`.

---

## STEP 5 — HOUSES (fields of life)

Read the priority houses (1, 7, 10, 4) plus any house holding a planet or the chart ruler.
For each: planets inside → sign on the cusp → **where the cusp ruler sits** (dispositor) →
aspects. Reference: `resources/houses.md`.

---

## STEP 6 — HERMETIC LAYER

Weave in the distinguishing European/Hermetic material:
- **Elemental & modal balance** (`balance`) — dominant/lacking element and modality =
  temperament (choleric/melancholic/sanguine/phlegmatic; cardinal/fixed/mutable emphasis).
- **Decans/faces** of the Sun, Moon, Ascendant for finer nuance (`resources/decans.md`).
- **Planetary day & hour of birth** (`hermetica`) — the presiding planetary signature
  (`resources/planetary-hours.md`). Pre-dawn births belong to the previous planetary day.
- **The Hermetic lots** (`lots`) — ⊕ Fortune (body & circumstance) and ⊗ Spirit (will &
  vocation), sect-aware; read sign, house, and the condition of each lot's ruler
  (`resources/lots.md`).
- **Solar condition** — name any cazimi/combust/under-beams planet and what it hides
  or crowns (`resources/planets.md`).
- **Nodes** — the growth axis (☊/☋). **Chiron is NOT computed** (de421 lacks it) —
  discuss only if the user supplies its position; never invent it.
- **Gnostic frame (optional):** the soul's descent/ascent through the seven spheres —
  dignities as planetary "garments", slow transits as "the sphere knocking", freedom
  through recognition (`resources/gnosis.md`). Offer as contemplation, never doctrine.
- Frame the whole through **"as above, so below"** and the relevant Hermetic principles
  (`resources/hermetic-principles.md`), integrating planet → sign → house → aspect →
  condition as ONE being, not a list.

---

## STEP 7 — METHOD-SPECIFIC ANALYSIS

Run only the block matching the requested **method**:

- **Natal** (default): full synthesis of Steps 2–6.
- **Transits:** cast a second chart for the target date; report current planets aspecting
  natal planets/angles (esp. Saturn, Jupiter, and the outer planets); give time windows.
- **Synastry (compatibility):** cast both charts, then run
  `py -3.13 compute/synastry.py chartA.json chartB.json --nameA "..." --nameB "..."`
  → JSON with `inter_aspects` (same orbs as natal, luminary bonus), `overlays_B_in_A` /
  `overlays_A_in_B` (house overlays), and `fit` (element/modality balances). ALSO run
  `compute/composite.py chartA chartB > composite.json` — every synastry reading contains
  a **KOMPOZYT — KARTA RELACJI** section (after the two-identities section): the midpoint
  chart's table (positions + houses from the composite AC), its 3–5 tightest aspects, and
  a short portrait of the relationship as a third entity (`resources/composite.md`).
  Interpret inter-aspects (Sun–Moon, Venus–Mars, Mercury–Mercury, node & angle contacts),
  the fit, the composite, and the overlays. Balanced, non-fatalistic — a map, never a
  verdict. HTML export: `compute/render_html_synastry.py chartA chartB synastry.json
  --composite composite.json --reading reading.md --lang pl --out reading.html`
  (two natal wheels + the composite wheel).
- **Synastry transits (relationship forecast):** how the sky activates the COUPLE.
  Three layers (see `resources/composite.md`): 1) `compute/composite.py chartA chartB`
  → midpoint composite chart; 2) `compute/synastry_transits.py chartA chartB
  synastry.json composite.json --from A --to B` → transits to the composite,
  "string activations" (a transit on one endpoint of a tight inter-aspect lights the
  whole string), lunations in composite houses; 3) reading = composite portrait + slow
  currents + relationship calendar + narrative. Save to
  `output/synastria/<A>_x_<B>_<date>_tranzyt-<okres>/`. HTML: add
  `--composite composite.json` to the synastry exporter (adds the relationship wheel).
- **Solar return (year-ahead):** chart for the moment the Sun returns to its natal degree
  in the target year; read its Ascendant, angular planets, and Moon for the year's themes.
  Compute Mode: find the moment by iterating — run the engine near the birthday, compare
  the Sun's `lon` to the natal value, and adjust `--dob`/`--tob` (the Sun moves ~1°/day ≈
  0°02.5'/hour; two or three runs converge to the minute).
- **Electional (planetary hours):** given an intention, recommend favorable day/hour rulers
  and Moon conditions (`resources/planetary-hours.md`).

---

## STEP 8 — SYNTHESIS & GUIDANCE

Integrate all layers into a coherent portrait. Priority when weighing:
```
Chart ruler & luminaries (Sun/Moon)  >  tight applying aspects & angular planets
   >  essential dignity & sect  >  house emphasis  >  minor aspects & decans
```
- Resolve contradictions **explicitly** ("the Mars square urges haste, but Saturn on the
  MC counsels patience — the growth is in pacing").
- **Language rules (mandatory):** speak of tendencies, invitations, and "the work of this
  placement" — never "you will." No fatalism, no fear ("danger", "doomed"), no exact-event
  or medical/legal/financial prediction. Give time windows as ranges. **Grammatical
  gender:** use the subject's known gender (confirmed by the user); when unknown, refer to
  the person through the Polish sign name and ITS grammatical gender ("Waga zrobiła",
  "Byk zrobił", "dziecko… jego") — never guess a person's gender. The chart is a mirror
  for self-knowledge (*gnōthi seauton*), not a verdict. See `resources/hermetic-principles.md`;
  for the ancient root of this stance (heimarmene binds only the unexamined life) and the
  reading-as-anamnesis frame, see `resources/gnosis.md`.
- **Step 8 structure (ALL readings):** three "· X ·" subsections: **· NARRACJA GWIAZD ·**
  → **· SYNTEZA ·** (the technical weave with glyphs) → **· WSKAZÓWKI ·** (concrete
  practices + the closing quote). The narracja is flowing prose with NO glyphs and no
  jargon, warm but non-flattering, every claim chart-anchored. Flavours by method:
  **NATAL — 450–700 words, second person, five movements** (flowing prose, no subheads):
  1) *wejście przez konkret* — open from one chart datum or a sensory detail, never a
  symmetrical portrait; 2) *mechanika wewnętrzna* — HOW the psyche runs: the dispositor
  chain told as an inner hierarchy ("kto komu oddaje klucze"), loops (receptions), the
  felt logic of the pattern; 3) *napięcie centralne* — the chart's core paradox held
  OPEN through at least one lived micro-scene (a meeting, a morning, a doorway), both
  poles shown working at once; 4) *cień* — the real cost of the pattern; at least one
  paragraph stays unsoftened, no instant reframe; 5) *ruch* — the development arc with
  a recognition test ("po czym poznasz, że…"); advice itself belongs to WSKAZÓWKI.
  Techniques: ONE chart-derived leitmotif image recurring 2–3 times and evolving; ≤2
  direct questions to the reader; time depth phrased as tendency (never biographical
  claims, never diagnoses); the author may briefly step in first-person ("nie będę tego
  wygładzał"). Depth comes from specificity and scenes, not ornament — all style.md
  budgets still bind.
  **SYNASTRIA — 250–400 words**, third person by name/sign (gender rules): how the two
  meet, what flows by itself, where they rub, ONE lived scene of the pair, what each
  learns from the other. **TRANZYTY — 200–300 words**: the weather of the period, its
  arc, one concrete scene; coarse timing only ("początek sierpnia") — dates stay in the
  calendar.
- **Prose style (mandatory):** follow the anti-slop budgets in `resources/style.md`
  (contrast/triad/aphorism limits, one chart-derived imagery domain per reading, stock
  metaphors banned, varied sentence rhythm, one unsoftened shadow). Before rendering,
  run `py -3.13 compute/style_check.py reading.md` and fix the warnings it reports.
- **Synthesis closer (mandatory style):** do not end Step 8 with the Hermetic motto — it
  already closes the disclaimer footer. Pick ONE theme-matched Nag Hammadi quote from the
  Closing-Quote Bank in `resources/gnosis.md` and attribute it (e.g. "Ewangelia Tomasza,
  log. 70"). Vary the quote across a person's readings.
- **Each reading is self-contained (mandatory):** treat every birth date as a separate
  individual. NEVER reference any other reading document — not other subjects' readings,
  not the same person's earlier readings, not alternative birth-time variants ("see the
  8:00 reading" / "jego odczyt mówi…" is forbidden). Alternative-hour comparisons inside
  a rectification reading are framed as data hypotheses ("przy godzinie 08:00"), never as
  pointers to another reading. Every chart fact a reading needs must be restated within
  it. Rectification analysis itself (event evidence, biographical dates, the word
  "rektyfikacja") never appears in a reading — the banner/PEWNOŚĆ state only the adopted
  vs recorded hour ("07:45 (przyjęta; zapisana 08:00)") and its chart-level sensitivity;
  the analysis stays in the conversation.

---

## STEP 9 — SAVE THE READING (output structure)

Persist every reading to a structured path under the project's `output/` directory.
**Individual readings** (natal / transits / solar-return / electional):

```
output/<zodiak>_<dob>/<dob>_<reading-date>_<method>_<purpose>/reading.md
```

- **`<zodiak>`** — the subject's tropical Sun sign in POLISH, lowercase, ASCII (no
  diacritics): `baran byk bliznieta rak lew panna waga skorpion strzelec kozioroziec→
  koziorozec wodnik ryby`.
- **`<dob>`** — birth date `YYYY-MM-DD`; **`<reading-date>`** — generation date.
- **`<method>`** — `natal` | `transits` | `solar-return` | `electional`.
- **`<purpose>`** — kebab-case, Polish (e.g. `ogolny`, `kariera`, `relacja`,
  `sierpien-wrzesien-2026`).

One folder per PERSON (`blizniata_1993-06-14/`) collects all their readings — no
collisions between different people who share a sign.

**Synastry** goes to its own tree:

```
output/synastria/<zodA>_<dobA>_x_<zodB>_<dobB>_<reading-date>_<purpose>/reading.md
```

Write the assembled report (from `templates/full-reading.md`) as `reading.md`; save the
raw engine JSON beside it as `chart.json` (`synastry.json` for synastry). Tell the user
the exact saved path. See `output/README.md` for the convention.

**Standard outputs: `reading.md` + `reading.html`. PDF ONLY when the user asks.**
```bash
py -3.13 compute/render_html.py chart.json --reading reading.md --lang pl \
    --out reading.html --title "..."
# PDF — na życzenie (on explicit request only), via headless Edge:
"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new \
    --disable-gpu --print-to-pdf="reading.pdf" --no-pdf-header-footer "file:///…/reading.html"
```
`render_html.py` produces a self-contained, accessible HTML report (SVG chart wheel,
semantic tables, balance bars, hermetic signature, lay-friendly hover/focus tooltips on
technical terms, the reading's prose) with a print stylesheet — it needs `chart.json`
and parses the prose out of `reading.md` automatically.

Example: a career natal reading generated 2026-08-06 for a Leo →
`output/2026-08-06/leo/natal/career/reading.md`.

---

## FINAL — DISCLAIMER FOOTER

End every reading with:
```
──────────────────────────────────────────
This reading is a Hermetic mirror for reflection and self-knowledge — a map of
tendencies and timing, not a prediction of fixed events. Astrology is a symbolic
tradition, not a substitute for professional medical, legal, psychological, or
financial advice. "As above, so below; know thyself."
──────────────────────────────────────────
```

---

## RESOURCE INDEX (load lazily, per step)

| File | Contains | Load for |
|------|----------|----------|
| `resources/planets.md` | 7 classical + 3 modern planets, sect, correspondences, rulerships | Steps 2, 3, 6 |
| `resources/signs.md` | Tropical signs, elements, modalities, polarity, keywords | Steps 1, 2 |
| `resources/houses.md` | 12 houses, angularity, house systems, dispositor logic | Steps 1, 5 |
| `resources/aspects.md` | Ptolemaic + minor aspects, orbs, patterns | Step 4 |
| `resources/dignities.md` | Essential dignities, terms, triplicities, scoring | Step 3 |
| `resources/decans.md` | 36 faces/decans (Chaldean + triplicity systems) | Step 6 |
| `resources/hermetic-principles.md` | "As above so below", 7 principles, ethics/stance | Steps 6, 8 |
| `resources/planetary-hours.md` | Chaldean order, day/hour rulers, election | Steps 6, 7 (electional) |
| `resources/lots.md` | Hermetic lots (⊕ Fortune, ⊗ Spirit) — formulas & reading | Step 6 |
| `resources/gnosis.md` | Christian-Gnostic layer: planetary garments, heimarmene, anamnesis | Steps 6, 8 |
| `resources/style.md` | anti-slop prose rules: budgets, imagery domains, rhythm | Step 8 |
| `compute/style_check.py` | prose linter — counts anti-pattern budgets in reading.md | Step 9 |
| `templates/full-reading.md` | Final report skeleton + geometry rules | Step 9 assembly |
| `compute/chart_engine.py` | Skyfield/de421 computation engine | Step 1 (Compute Mode) |
| `compute/render_chart.py` | Renders chart.json → finished report tables (en/pl) | Steps 1, 9 |
| `compute/render_html.py` | chart.json + reading.md → accessible HTML (SVG wheel) | Step 9 (export) |
| `compute/synastry.py` | two chart.json → inter-aspects, overlays, fit | Step 7 (synastry) |
| `compute/render_html_synastry.py` | synastry HTML (two wheels; `--composite` adds third) | Steps 7, 9 |
| `resources/composite.md` | composite chart & relationship transits — how to read | Step 7 |
| `compute/composite.py` | two chart.json → midpoint composite chart | Step 7 (syn. transits) |
| `compute/synastry_transits.py` | transits to composite + string activations + lunations | Step 7 (syn. transits) |
