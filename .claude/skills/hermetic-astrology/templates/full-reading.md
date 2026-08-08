# Hermetic Astrology Reading — Output Template (v2)

Assemble the final report from the SKELETON below. Fill every `[bracket]` from the
pipeline steps (SKILL.md Steps 0–8); section numbers 1–8 match the pipeline steps.
Write the report in **the user's language** — translate all labels, keep the structure.

**Compute Mode shortcut:** the data sections (1, 3, 4 tables + balance bars + the
hermetic signature panel) are produced verbatim by the renderer —

```bash
py -3.13 compute/render_chart.py path/to/chart.json --lang pl   # or en
```

— paste its output into the skeleton and write only the prose around it. Never
hand-align tables when the renderer is available. In Prompt Mode imitate the same
geometry by hand.

Save the report as plain text in `reading.md`. When showing it in chat, wrap the
report in one fenced code block so the box art stays monospace.

## Geometry & alignment rules (Prompt Mode / prose sections)

1. **Global width = 72.** Box borders and section rules are exactly 72 chars;
   prose wraps at ≤ 74. Footer rules are 42 × `─`.
2. **Every glyph counts as ONE column** (☉ ♎ △ ° ′ ⊕ █ ░). Align by character
   count; never add compensation spaces.
3. **Numbers:** degrees `d°mm′`; orbs one decimal (`0.6°`); dignity scores with
   explicit sign and true minus (`+5`, `−9`); houses in Roman numerals (I…XII).
4. Empty cell = spaces · unknown value = `—`.

## Glyph legend

| Planets | ☉ Sun · ☽ Moon · ☿ Mercury · ♀ Venus · ♂ Mars · ♃ Jupiter · ♄ Saturn · ♅ Uranus · ♆ Neptune · ♇ Pluto |
|---|---|
| Points | ☊ North Node · ☋ South Node · ⊕ Lot of Fortune · ⊗ Lot of Spirit · AC · MC |
| Signs | ♈♉♊♋♌♍♎♏♐♑♒♓ |
| Aspects | ☌ 0° · ⚺ 30° · ∠ 45° · ⚹ 60° · Q 72° · □ 90° · △ 120° · ⚻ 150° · ☍ 180° |
| Motion | `Rx` retrograde · phase `a` applying / `s` separating / `e` exact (translate) |

## Data mapping (chart.json → skeleton)

- Sections 1/3/4 + bars + panel 6: renderer output (see above).
- Solar condition: `planets.*.solar_condition` (cazimi ≤ 0°17′ · combust ≤ 8°30′ ·
  under beams ≤ 15°). Sect status: `planets.*.sect_status`. Lots: `lots.Fortune` /
  `lots.Spirit`. Aspects to AC/MC are in `aspects[]` (phase `—`).
- Chiron is NOT computed (de421 lacks it) — omit its line, never invent it.
- Unknown birth time → houses column `—`, AC/MC `unknown`, omit Lots & section 5,
  confidence Low.

## Method matrix

| Section | natal | transits | synastry | solar-return | electional |
|---|---|---|---|---|---|
| Banner + meta | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1 Chart + bars | ✓ | ✓ (natal) | ✓ ×2 (label per person) | ✓ (natal) | event chart if any |
| 2 Core identity | ✓ | ✓ (brief) | ✓ ×2 (2–3 lines each) | ✓ (brief) | omit |
| 3 Dignity & condition | ✓ | ✓ | key lines per person | ✓ | election ruler/Moon |
| 4 Aspect grid + list | ✓ | ✓ (natal) | inter-aspects in 7C | ✓ (natal) | omit |
| 5 Houses | ✓ | ✓ (brief) | omit (overlays in 7C) | omit (in 7D) | omit |
| 6 Hermetic layer | ✓ | ✓ | ✓ (both, compact) | ✓ | day/hour in 7E |
| 7 Method focus | 7A | 7B | 7C | 7D | 7E |
| 8 Synthesis + confidence + footer | ✓ | ✓ | ✓ | ✓ | ✓ |

Keep **only** the matching 7A–7E block and retitle its rule to 72 chars.

---

## THE SKELETON

```
╔══════════════════════════════════════════════════════════════════════╗
║ ☉ ☽ ☿ ♀ ♂ ♃ ♄   H E R M E T I C   A S T R O L O G Y   ♅ ♆ ♇ ☊ ⊕      ║
║                                                                      ║
║ [METHOD] READING — "As above, so below"                              ║
╚══════════════════════════════════════════════════════════════════════╝
  Subject    : [Name]
  Born       : [DD Month YYYY] · [HH:MM] ([exact / approx / noon])
  Place      : [City, Country] · [lat]°[N/S] [lon]°[E/W] · UTC[±h]
  Zodiac     : Tropical (of date) · Houses: [effective system] · Sect: [Day ☉/Night ☽]
  Generated  : [YYYY-MM-DD] · Method: [natal/…] · Purpose: [general/…]
  Mode       : [Compute — Skyfield / JPL de421 | Prompt — approximate]
────────────────────────────────────────────────────────────────────────

[RENDERER SECTION 1 — chart table + chart-ruler line + balance bars]
→ [one line: dominant/lacking element & modality · temperament]

─── 2 · CORE IDENTITY ──────────────────────────────────────────────────
☉ SUN in [sign] · house [N] — [2–3 sentences: vital purpose]
☽ MOON in [sign] · house [N] — [2–3 sentences: needs, instinct]
AC [sign] — chart ruler [planet] in [sign] · house [N] —
   [2–3 sentences: temperament; how the ruler steers the nativity]
SYNTHESIS — [3–5 sentences weaving the keystones into one portrait]

[RENDERER SECTION 3 — dignity & condition table]
KEY — strongest: [planet(s)] · most strained: [planet(s)] · [solar notes]

[RENDERER SECTION 4 — aspect grid + key-aspect list]
 [after each listed aspect, or below the list: one line of meaning for
  the 4–8 aspects that matter most — luminaries, angles, chart ruler]
CONFIGURATIONS — [stellium / T-square / grand trine / yod / none prominent]

─── 5 · HOUSES ─────────────────────────────────────────────────────────
I    SELF & BODY [(sign)]       — [2–3 sentences]
VII  RELATIONSHIP [(sign)]      — [2–3 sentences]
X    VOCATION — MC [(sign)]     — [2–3 sentences]
IV   HOME & ROOTS — IC [(sign)] — [2–3 sentences]
[+ any house holding a stellium, the chart ruler, or the method's focus]

[RENDERER SECTION 6 — hermetic signature panel]
"As above, so below" — [1–2 sentences uniting the layers into one theme]

─── 7 · METHOD FOCUS — [METHOD] ────────────────────────────────────────
[Keep ONLY the chosen method's block:]

· 7A NATAL ·
[No table. Deepen the synthesis: the life arc in 4–6 sentences — the
 tension the chart keeps returning to, and the faculty that resolves it.]

· 7B TRANSITS — for [date] ·
┌────────────────┬─────┬─────────────┬──────┬──────────────────────────┐
│ Transit        │ Asp │ Natal       │ Orb  │ Window / note            │
╞════════════════╪═════╪═════════════╪══════╪══════════════════════════╡
│ [♄ Saturn d°♈] │ [☍] │ [☉ Sun]     │ [orb]│ [when it peaks · tone]   │
└────────────────┴─────┴─────────────┴──────┴──────────────────────────┘
[Narrative: 2–4 dominant storylines, slow planets first, windows as
 ranges. Close with the single headline of the period.]

· 7C SYNASTRY — [A] ✕ [B] ·
┌────────────────────┬─────┬────────────────────┬──────┬───────────────┐
│ [A] point          │ Asp │ [B] point          │ Orb  │ Tone          │
╞════════════════════╪═════╪════════════════════╪══════╪═══════════════╡
│ [☉ Sun d°♎]        │ [△] │ [☽ Moon d°♒]       │ [orb]│ [harmonious]  │
└────────────────────┴─────┴────────────────────┴──────┴───────────────┘
[Element fit · house overlays · the gift and the friction of the bond.]

· 7D SOLAR RETURN — year [YYYY–YYYY] ·
[SR moment used · SR Ascendant + ruler · angular planets · SR Moon →
 the year's 2–3 themes, each with its season.]

· 7E ELECTIONAL — [intention] ·
┌────────────┬────────────┬────────────────┬────────────────────┬──────┐
│ Date       │ Day ruler  │ Hour of        │ Moon               │ Fit  │
╞════════════╪════════════╪════════════════╪════════════════════╪══════╡
│ [date]     │ [♃ Jupiter]│ [♀ Venus, 3rd] │ [♋ Cancer, waxing] │ [★★★]│
└────────────┴────────────┴────────────────┴────────────────────┴──────┘
[Why these windows serve the intention; what to avoid. 2–3 windows.]

─── 8 · SYNTHESIS & GUIDANCE ───────────────────────────────────────────
[5–8 sentences integrating every layer. Resolve contradictions
 explicitly. Name the central life-theme and the work it invites.
 Probabilistic, empowering language — tendencies, never "you will".]

┌─ CONFIDENCE ──────────────────────────────────────────────────────────
│ Birth time : [High/Med/Low] — [reason]
│ Location   : [High/Med] — [reason]
│ Positions  : [High (computed, Skyfield/de421) / Medium (Prompt Mode)]
│ Overall    : [High/Med/Low] · [caveats]
└───────────────────────────────────────────────────────────────────────

──────────────────────────────────────────
This reading is a Hermetic mirror for reflection and self-knowledge — a
map of tendencies and timing, not a prediction of fixed events. Astrology
is a symbolic tradition, not a substitute for professional medical,
legal, psychological, or financial advice.
"As above, so below; know thyself."
──────────────────────────────────────────
```

Translate the footer faithfully into the reading's language; keep both 42-char rules.
