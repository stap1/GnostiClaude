# Style — Anti-Slop Rules for Reading Prose (mandatory)

Readings must not read like generic model output. The data layer (orbs,
dignities, houses) carries authority by itself; the prose must carry a human
voice. These rules are countable budgets, not vibes — check them before
rendering (`compute/style_check.py reading.md` automates most of it).

## Hard budgets (per reading)

| Pattern | Budget | Note |
|---|---|---|
| "nie X, lecz/tylko/a Y" contrast | ≤ 1 | NEVER as a paragraph's closing line |
| Triads ("A, B i C" rhythm) | ≤ 2 | prefer uneven lists: two items, four, one cut short |
| Aphorism / bon mot as paragraph closer | ≤ 1 per subsection | most paragraphs end plainly, mid-register |
| "co do minuty/ćwierci stopnia" wow-phrases | ≤ 1 | the orb number already impresses |
| Exclamation marks in tables | ≤ 1 | |
| Scare quotes around ordinary words („ja", „my", „u siebie") | ≤ 3 | |
| Em-dash asides | ≤ 1 per sentence | vary with parentheses, commas, or a new sentence |

## Sentence rhythm

Every NARRACJA must contain at least one sentence of ≤ 5 words and at least
one of > 30 words. If three consecutive sentences have the same two-clause
shape, rewrite one. Read the paragraph aloud mentally; if it swings like a
metronome, break the beat.

## Imagery: one domain, from the chart

Before writing Step 8, pick ONE metaphor domain derived from the chart itself
(dominant element, sign, or strongest dignity) and stay inside it:

- Byk/Ziemia — ogród, kuchnia, rzemiosło stołu
- Strzelec/Ogień — droga, łuk, ognisko
- Koziorożec — kamień, góry, mur
- Ryby/Woda — przypływ, port, nurt
- Bliźnięta/Powietrze — listy, mapy, rozmowa w drodze
- Lew — scena tylko jeśli karta ją niesie; inaczej: dwór, złoto, południe

**Blocklist (dyżurne metafory — do not use):** mgła*, iskra, silnik,
warsztat/pracownia, kuźnia, sad, drabina, koło zamachowe, huśtawka,
„wiatr w plecy/kurs", „powietrze dmie w ogień", zamek bez drzwi/fundamentów.
(*Neptune may be named as Neptun/sen/rozmycie — not „mgła" by default.)
Never repeat a coined image across the same person's readings.

## Structural anti-templates

- NARRACJA must NOT open with a symmetrical two-portrait ("On X, ona Y").
  Open from one concrete chart datum (a degree, an hour, a dignity) or a
  sensory observation.
- DAR does not have to come in "piętra/three floors"; CIEŃ paragraphs: at
  least ONE difficulty per reading stays stated without an immediate
  softening reframe.
- Kalendarium "Ton" column: verb phrases and empty cells allowed; not every
  row needs a noun punchline.
- Voice follows the chart: air-dominant subject → shorter, matter-of-fact
  sentences; earth → concrete nouns, few adjectives; water → longer arcs;
  fire → verbs. Two different subjects' readings must not sound identical.

## Engine visibility — the skeleton principle

The technical apparatus is the movement of a skeleton watch: visible, even
beautiful, but never louder than the dial.

- **Orbs in prose:** the exact figure appears at ≤3 load-bearing claims per
  reading; elsewhere write "ścisły", "luźny", "na granicy orbu". Full
  precision lives in the MECHANIZM annex — the prose narrates, the annex
  certifies. (The HTML additionally sets in-prose figures in a quiet
  `datum` style.)
- **Signatures in flow, tables in the annex:** between the wheel and the
  interpretation only compact signatures travel (the chips row, one-line
  "heartbeat" of ruler · sect · tightest aspects). Position/dignity/aspect
  tables belong to the collapsed MECHANIZM section at the end of the page;
  in HTML the wheel's chords carry hover tooltips with aspect + orb, so the
  springs can be inspected without opening the case-back.
- **Synastry follows the same watch:** `render_html_synastry.py` keeps
  wheels → identities → composite → reading on the dial; the inter-aspect
  table, house overlays and the FOKUS METODY commentary (chart-fit,
  DAR/CIEŃ datum walk-through) fold into the same collapsed MECHANIZM
  annex.
- **Never start a prose line with a glyph, `AC `/`MC `, `→` or `„`:** the
  exporter treats those as list markers and splits the paragraph there.
  Reflow the line (`jego Księżyc siada na jej Wenus (☽A ☌ ♀B)` instead of
  a line opening with `☽A`). Deliberate list items — the `→` lines under a
  table — are exactly what the rule is for, so leave those alone.

## NARRACJA by method (Step-8 spec)

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
wygładzał"). Depth comes from specificity and scenes, not ornament — all budgets
above still bind.

**SYNASTRIA — 250–400 words**, third person by name/sign (gender rules in SKILL.md
Step 8): how the two meet, what flows by itself, where they rub, ONE lived scene of
the pair, what each learns from the other.

**TRANZYTY — 200–300 words**: the weather of the period, its arc, one concrete scene;
coarse timing only ("początek sierpnia") — dates stay in the calendar.

## What stays

Data anchoring (every claim traceable to a placement), Polish astrological
terminology, the section skeleton, Nag Hammadi closers, the ethics rules.
Style discipline serves credibility — the reading should sound like a
practitioner who writes, not a generator that patterns.
