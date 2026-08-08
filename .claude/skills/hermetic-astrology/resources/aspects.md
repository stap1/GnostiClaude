# Aspects — The Geometry of Relationship

Aspects are the angular relationships between planets — the chart's "wiring." They
are the central predictive/interpretive mechanism of Western astrology (and the
biggest technical difference from the Vedic house-based aspect system). An aspect is
counted when two bodies are within **orb** of an exact angle.

## Major (Ptolemaic) Aspects

| Aspect | Glyph | Angle | Default Orb | Nature | Meaning |
|--------|-------|-------|-------------|--------|---------|
| **Conjunction** | ☌ | 0° | 8° | Fusion | Blending, intensification — depends on the planets |
| **Opposition** | ☍ | 180° | 8° | Tension | Polarity, awareness through the Other, projection |
| **Trine** | △ | 120° | 8° | Harmony | Ease, talent, natural flow (same element) |
| **Square** | □ | 90° | 7° | Friction | Challenge, drive, growth through obstacle |
| **Sextile** | ⚹ | 60° | 6° | Opportunity | Support, potential requiring effort to activate |

## Minor Aspects

| Aspect | Glyph | Angle | Orb | Meaning |
|--------|-------|-------|-----|---------|
| **Quincunx / Inconjunct** | ⚻ | 150° | 3° | Adjustment, mismatch, chronic tweaking |
| **Semisextile** | ⚺ | 30° | 2° | Mild friction between neighbors |
| **Semisquare** | ∠ | 45° | 2° | Minor irritation, subsurface tension |
| **Sesquiquadrate** | ⚼ | 135° | 2° | Agitation, crisis of activity |
| **Quintile** | Q | 72° | 2° | Creative gift, unique talent (Keplerian) |

## Orbs — refinements
- **Luminaries (Sun, Moon)** warrant wider orbs. The engine adds **+2°** to the
  major aspects (0/60/90/120/180°) when either body is the Sun or Moon.
- **Tighter orb = stronger aspect.** An aspect within 1° is dominant; near the orb
  limit it is faint.
- **Applying vs. separating:** the aspect is **applying** when the *orb to exact*
  is shrinking (building, future-oriented, stronger in prediction) and
  **separating** when it grows (fading, past-oriented). The engine computes this
  from the true rate of change of the orb (`phase`: applying/separating/exact).
- **Aspects to the angles:** the engine also reports aspects to the Ascendant and
  Midheaven (phase `—`, as natal angles are static reference points). Weight them
  like aspects to a luminary.

## Dignities of aspect (traditional)
- Planets in **trine/sextile** are in signs of compatible element → they "regard" each
  other kindly.
- Planets in **square/opposition** are in signs of hard relationship → they strain.
- **Conjunction** is neither harmonious nor hard by itself — read the planets and
  their condition (e.g. Venus☌Jupiter is benefic; Mars☌Saturn is hard).
- **Aversion:** planets in signs that form NO Ptolemaic aspect (30°/150° apart by
  sign) are "averse" — they cannot see each other, a subtle blind spot.

## Aspect Patterns (configurations)
| Pattern | Structure | Meaning |
|---------|-----------|---------|
| **Stellium** | 3+ planets conjunct / in one sign or house | Massive concentration of focus in that area |
| **Grand Trine** | 3 planets in trine (a triangle, one element) | Great ease/talent, can be complacent |
| **T-Square** | 2 planets opposed, both square a third (apex) | Dynamic tension driving action; apex = pressure point |
| **Grand Cross** | 4 planets in two oppositions, all square | Intense, four-way tension, great capacity under strain |
| **Yod** | 2 planets sextile, both quincunx a third (apex) | "Finger of fate" — a fated adjustment, special mission |
| **Kite** | Grand trine + one planet opposing a corner | Grand-trine talent given an outlet/direction |
| **Mystic Rectangle** | 2 oppositions linked by trines & sextiles | Balanced tension, practical use of opposites |

## How to weight aspects
1. Aspects to the **Sun, Moon, Ascendant ruler, and chart angles** matter most.
2. **Applying, tight** aspects outrank wide, separating ones.
3. Read the **planets' condition** (dignity, sect, house) before judging an aspect
   good or bad — a "hard" aspect between dignified planets can be highly productive.
