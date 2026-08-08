# Planets — The Seven Classical + Three Modern

The seven classical (visible) planets are the backbone of Hermetic and traditional
Western astrology. The three modern (trans-Saturnian) planets are used as
generational/transpersonal overlays. The lunar Nodes and Chiron are sensitive points.

## The Seven Classical Planets (Hermetic core)

| Planet | Glyph | Principle | Governs | Metal | Day | Keyword |
|--------|-------|-----------|---------|-------|-----|---------|
| **Sun** ☉ | Solar | Vital spirit, the Self | Identity, vitality, purpose, father, authority | Gold | Sunday | "I will" |
| **Moon** ☽ | Lunar | Reflective soul | Emotions, instinct, habit, mother, the body, public | Silver | Monday | "I feel" |
| **Mercury** ☿ | Hermetic | Mind & messenger | Thought, speech, commerce, learning, hands | Quicksilver | Wednesday | "I think" |
| **Venus** ♀ | Concord | Love & harmony | Attraction, art, values, pleasure, relationship | Copper | Friday | "I value" |
| **Mars** ♂ | Discord | Will & force | Drive, courage, aggression, desire, cutting | Iron | Tuesday | "I act" |
| **Jupiter** ♃ | Expansion | Grace & growth | Wisdom, abundance, faith, law, generosity | Tin | Thursday | "I expand" |
| **Saturn** ♄ | Limitation | Time & structure | Discipline, boundaries, karma, endurance, bones | Lead | Saturday | "I master" |

### Sect (day/night) — a traditional distinction
- **Diurnal planets:** Sun, Jupiter, Saturn — favored in day charts.
- **Nocturnal planets:** Moon, Venus, Mars — favored in night charts.
- **Mercury** is common (diurnal if it rises before the Sun, nocturnal if after).
- **Benefics:** Jupiter (greater), Venus (lesser). **Malefics:** Saturn (greater), Mars (lesser).
- A benefic **of the sect** is at its most helpful; a malefic **contrary to the sect**
  is at its most difficult. Always read planets in light of chart sect.

## The Three Modern Planets (transpersonal)

| Planet | Glyph | Principle | Governs | Co-rules |
|--------|-------|-----------|---------|----------|
| **Uranus** ♅ | Awakening | Disruption, freedom, genius, revolution, sudden change | Aquarius |
| **Neptune** ♆ | Dissolution | Imagination, mysticism, illusion, compassion, the ideal | Pisces |
| **Pluto** ♇ | Regeneration | Power, death/rebirth, the underworld, deep transformation | Scorpio |

> In strict traditional practice the modern planets do not rule signs or receive
> dignity. Use them for depth psychology and generational themes; anchor
> predictive/dignity work in the classical seven.

## Sensitive Points

| Point | Glyph | Meaning |
|-------|-------|---------|
| **North Node** ☊ | Growth edge, the soul's forward direction, what to develop |
| **South Node** ☋ | Innate gifts, past patterns, what to release |
| **Chiron** ⚷ | The "wounded healer" — the deep wound that becomes a source of healing |
| **Lot of Fortune** ⊕ | Body & circumstance — the sect-aware lunar lot (see lots.md) |
| **Lot of Spirit** ⊗ | Will & vocation — the sect-aware solar lot (see lots.md) |
| **Ascendant** (ASC) | The body, temperament, the mask, the point of incarnation |
| **Midheaven** (MC) | Vocation, public standing, the aim of the life |

> **Chiron is not computed by the engine** (the de421 ephemeris lacks it). Discuss
> Chiron only if the user supplies its position from another source — never invent it.

## Planetary Speed & Condition

- **Retrograde** (apparent backward motion): the planet's function turns inward,
  is revisited, or works unconventionally. The Sun and Moon are never retrograde.
- **Combustion:** a planet within ~8°30' of the Sun is "combust" — overwhelmed and
  weakened. Within ~17' it is **cazimi** ("in the heart of the Sun") — greatly strengthened.
- **Under the beams:** within ~15° of the Sun — mildly weakened.
- **Stationary** (speed near zero): the planet's themes are emphasized and concentrated.

> The engine computes all of this: `solar_condition` (cazimi / combust /
> under beams / free) with `elongation_deg` for every body except the Sun, plus
> signed `speed` (deg/day) and the `retrograde` flag from a centered difference.

## Dignity Rulerships (used for essential dignity — see dignities.md)

| Planet | Domicile | Exaltation | Detriment | Fall |
|--------|----------|------------|-----------|------|
| Sun | Leo | Aries 19° | Aquarius | Libra |
| Moon | Cancer | Taurus 3° | Capricorn | Scorpio |
| Mercury | Gemini, Virgo | Virgo 15° | Sagittarius, Pisces | Pisces |
| Venus | Taurus, Libra | Pisces 27° | Aries, Scorpio | Virgo |
| Mars | Aries, Scorpio | Capricorn 28° | Libra, Taurus | Cancer |
| Jupiter | Sagittarius, Pisces | Cancer 15° | Gemini, Virgo | Capricorn |
| Saturn | Capricorn, Aquarius | Libra 21° | Cancer, Leo | Aries |

## Hermetic Correspondences (as above, so below)

Each classical planet threads through the whole chain of being — metal, day, tone,
color, plant, part of the body. This is the doctrine of **correspondences**: the
seven planetary powers repeat at every level of nature (see hermetic-principles.md
and planetary-hours.md). When interpreting, a planet is not only "in a sign" — it is
a single force expressing through metal, hour, organ, and psyche at once.
