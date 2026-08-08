# Wyniki odczytów astrologicznych

Każdy odczyt skilla **hermetic-astrology** trafia tu według konwencji:

## Odczyty indywidualne (natal, transits, solar-return, electional)

```
output/<zodiak>_<data-urodzenia>/<data-urodzenia>_<data-odczytu>_<metoda>_<cel>/
```

| Segment | Znaczenie | Przykład |
|---------|-----------|----------|
| `<zodiak>` | Znak słoneczny po polsku, małymi literami, bez znaków diakrytycznych | `wodnik`, `waga`, `baran`, `bliznieta` |
| `<data-urodzenia>` | `RRRR-MM-DD` | `1993-06-14` |
| `<data-odczytu>` | Data wygenerowania, `RRRR-MM-DD` | `2026-08-07` |
| `<metoda>` | `natal` · `transits` · `solar-return` · `electional` | `natal` |
| `<cel>` | kebab-case, po polsku | `ogolny`, `kariera`, `sierpien-wrzesien-2026` |

Przykład: `output/blizniata_1993-06-14/1993-06-14_2026-08-07_natal_ogolny/`

Folder osoby (`blizniata_1993-06-14/`) gromadzi wszystkie jej odczyty — kolejne
tranzyty, rewolucje słoneczne itd. lądują obok siebie.

## Synastrie

```
output/synastria/<zodiakA>_<dataA>_x_<zodiakB>_<dataB>_<data-odczytu>_<cel>/
```

Przykład: `output/synastria/blizniata_1993-06-14_x_skorpion_1995-11-08_2026-08-07_relacja/`

## Zawartość folderu odczytu

Standardowo (zawsze):

- `reading.md` — raport tekstowy (72 kolumny, ramki)
- `reading.html` — eksport HTML z kołem SVG (samodzielny plik)
- `chart.json` — surowy wynik silnika (`synastry.json` dla synastrii;
  kompozyt/tranzyty relacji: `composite.json` + `transits.json`)

Tylko na wyraźne życzenie użytkownika:

- `reading.pdf` — wersja do druku (headless Edge z `reading.html`)
- kopia HTML/PDF pod opisową nazwą (np. `blizniata_1993_natal_ogolny.html`) — do
  wysłania/udostępnienia
