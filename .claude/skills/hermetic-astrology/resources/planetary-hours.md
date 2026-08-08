# Planetary Days & Hours — Hermetic Timing (Election)

Planetary hours are the classic Hermetic tool for **timing** — choosing the moment
whose ruling planet favors an intention ("election"), and adding a layer of meaning
to a birth moment. Rooted in the *Picatrix* and Agrippa, they rest on the Principle
of Rhythm (see hermetic-principles.md). The engine reports the planetary **day ruler**
and **hour ruler** of any birth or query moment.

## The Chaldean Order
All planetary-hour reckoning uses the Chaldean order — the seven classical planets
from slowest to fastest:

> **Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon** → (repeat)

## Rulers of the Days of the Week

| Day | Ruler | Glyph |
|-----|-------|-------|
| Sunday | Sun | ☉ |
| Monday | Moon | ☽ |
| Tuesday | Mars | ♂ |
| Wednesday | Mercury | ☿ |
| Thursday | Jupiter | ♃ |
| Friday | Venus | ♀ |
| Saturday | Saturn | ♄ |

## How Planetary Hours Work
1. A planetary "day" runs from **sunrise to sunrise**, not midnight to midnight.
2. Daytime (sunrise→sunset) is split into **12 equal "hours"**; nighttime
   (sunset→next sunrise) into 12 more. These hours are **unequal** and vary with season
   and latitude (long day-hours in summer, short in winter).
3. The **first hour after sunrise is ruled by the day's planet** (e.g. Sunday's first
   hour = Sun). Each following hour is the next planet in Chaldean order, cycling
   continuously through day and night.

Because 24 is not a multiple of 7, the day's ruler always ends up ruling its own first
hour — which is precisely why the days fall in their familiar order.

> **Births between midnight and sunrise** belong to the PREVIOUS day's planetary day
> (hours 13–24 of its sequence, measured from the previous sunset). The engine
> handles this automatically — a 03:00 Thursday birth is in Wednesday's (Mercury's)
> planetary day.

## Electional use — choosing a good moment
Match the planet to the intention:

| Intention | Favored planet(s) | Notes |
|-----------|-------------------|-------|
| Career, honor, leadership, vitality | **Sun** | Sunday; Sun hour |
| Home, emotions, travel, the public | **Moon** | Monday; waxing Moon for growth |
| Study, contracts, writing, trade, messages | **Mercury** | Wednesday; avoid retrograde Mercury |
| Love, art, beauty, reconciliation, money | **Venus** | Friday; Venus hour |
| Courage, competition, surgery, decisive action | **Mars** | Tuesday; use with care |
| Growth, wealth, law, teaching, generosity | **Jupiter** | Thursday; Jupiter hour |
| Discipline, endings, real estate, long-term structure | **Saturn** | Saturday; deliberate work |

**Electional refinements:** prefer the planet **strong by sign and dignity**
(dignities.md), **applying to benefics**, and **not combust or retrograde**; align the
day AND the hour when possible; consider the Moon's phase and sign.

## In a natal reading
Report the **planetary day ruler** and **planetary hour ruler** of birth as an extra
Hermetic signature — it reinforces (or counterpoints) the chart ruler and Sun/Moon,
and hints at the "hour-genius" presiding over the incarnation.

> Note: planetary-hour lengths depend on true local sunrise/sunset. The engine
> computes them ephemeris-based (Skyfield almanac — accurate to seconds at normal
> latitudes). Above the polar circles during polar day/night the planetary hours
> are undefined and the engine reports only the day ruler.
