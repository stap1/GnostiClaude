# Hermetic Lots (Arabic Parts) — Fortune & Spirit

The lots are calculated points — not bodies — central to Hellenistic and Arabic
astrology and carried through the Hermetic tradition (Dorotheus, Vettius Valens,
Abu Ma'shar, the *Picatrix*). Each lot projects the arc between two significators
from the Ascendant. The engine computes the two primary lots, **sect-aware**.

## Formulas (zodiacal longitudes; both reverse by sect)

| Lot | Day chart | Night chart | Principle |
|-----|-----------|-------------|-----------|
| **⊕ Fortune** (Tyche) | ASC + Moon − Sun | ASC + Sun − Moon | The body & circumstance — health, livelihood, the fortune that *happens to* you |
| **⊗ Spirit** (Daimon) | ASC + Sun − Moon | ASC + Moon − Sun | The soul & initiative — career of the will, what you *do* deliberately |

Fortune is the lunar lot (what befalls), Spirit the solar lot (what one wills) —
a perfect polarity pair for the Hermetic frame ("that which is below" and "that
which is above" within one nativity).

## How to read a lot

1. **Sign & house** — the arena where fortune (or deliberate spirit) concentrates.
   The house of Fortune is a de-facto second "1st house" for material matters.
2. **The lot's ruler** (domicile lord of its sign) — its condition (dignity,
   house, aspects) shows *how* that fortune is administered. A dignified ruler
   of Fortune = resources come together; an afflicted one = fortune leaks.
3. **Planets conjunct or aspecting the lot** — benefics improve, malefics strain.
4. In **annual work** (solar returns, transits) a transit to natal Fortune often
   times material/circumstantial shifts; to Spirit — vocational/volitional ones.

Engine output: `lots.Fortune` and `lots.Spirit`, each with `position`, `sign`,
`house`, and `ruler`.

> Many more lots exist (Eros, Necessity, Courage, Nemesis, marriage lots, etc.).
> Compute them on request with the same projection logic: Lot = ASC + B − A
> (day), reversed by night — "from A to B, projected from the Ascendant."
