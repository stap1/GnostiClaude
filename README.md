# Astrologia — hermetyczny silnik astrologiczny (Claude Skill)

**Astrologia zachodnia (tropikalna) na fundamencie hermetycznym**, opakowana w skill
dla [Claude Code](https://claude.com/claude-code). Liczy karty z dokładnością
efemeryd JPL, interpretuje w duchu tradycji klasycznej („jak na górze, tak na dole")
i zapisuje piękne raporty — tekstowe oraz HTML z kołem horoskopu SVG.

> Tradycja klasyczna/europejska w pełnym aparacie: zodiak tropikalny (bez ayanamsy),
> aspekty ptolemejskie, godności esencjalne z sektą, terminy egipskie, oblicza
> chaldejskie, loty hermetyczne i godziny planetarne.

## Możliwości (6 metod odczytu)

| Metoda | Co daje |
|---|---|
| **natal** | pełny horoskop urodzeniowy: pozycje, godności+sekta, aspekty, domy, loty ⊕⊗, dekany, godziny planetarne, synteza |
| **transits** | prognoza na wybrany okres: skan efemerydy co 6 h, kalendarium ścisłych dat, ingresy, stacje, nowie/pełnie/zaćmienia |
| **synastry** | dopasowanie dwojga: interaspekty, nakładki domów, zgodność żywiołów |
| **synastry-transits** | tranzyty RELACJI: karta kompozytowa (midpointy), „aktywacje strun" interaspektów, lunacje w domach kompozytu |
| **solar-return** | rewolucja słoneczna — tematy roku |
| **electional** | wybór terminu: dni i godziny planetarne, kondycja Księżyca |

## Jak używać

W Claude Code, w katalogu projektu, po prostu poproś (po polsku lub angielsku).
Wszystkie daty poniżej są fikcyjne — to tylko przykłady składni:

```
wygeneruj natal 14.06.1993, godz. 15:40, Gdańsk, Polska
tranzyty dla bliźniąt 1993 na marzec–kwiecień 2027
synastria bliźnięta 1993 × skorpion 1995
tranzyt relacji bliźnięta × skorpion na 2027
```

Samo wywołanie skilla bez zadania pokazuje **menu powitalne** z siedmioma
opcjami (natal, tranzyty, synastria, kompozyt, rewolucja słoneczna, elekcja)
— w tym skrót **„tranzyty [data]"**: błyskawiczna pogoda dnia dla Twojej
karty na wskazany dzień kalendarzowy (domyślnie dziś).

Claude uruchomi silnik, złoży interpretację i zapisze wyniki w `output/`.
Standardowo powstają **`reading.md` + `reading.html`** (PDF na życzenie).

### Bezpośrednio z CLI (bez interpretacji)

```bash
# instalacja zależności (raz; czysty Python — bez kompilatora)
py -3.13 -m pip install -r .claude/skills/hermetic-astrology/requirements.txt

# karta natalna → JSON (data przykładowa)
py -3.13 .claude/skills/hermetic-astrology/compute/chart_engine.py \
  --dob 1993-06-14 --tob 15:40 --lat 54.35 --lon 18.65 --tz 2

# tabele raportu (PL/EN)   |   eksport HTML z kołem SVG
py -3.13 .../compute/render_chart.py chart.json --lang pl
py -3.13 .../compute/render_html.py chart.json --reading reading.md \
  --lang pl --out reading.html

# synastria, kompozyt, tranzyty relacji
py -3.13 .../compute/synastry.py chartA.json chartB.json
py -3.13 .../compute/composite.py chartA.json chartB.json
py -3.13 .../compute/synastry_transits.py chartA chartB synastry.json \
  composite.json --from 2026-08-01 --to 2026-09-30
```

Pierwsze uruchomienie pobiera efemerydę `de421.bsp` (~17 MB, zakres 1900–2049).
Bez Pythona skill działa w trybie promptowym (przybliżenia liczone przez model).

## Architektura

```
.claude/skills/hermetic-astrology/
├── SKILL.md                    # orkiestracja: wyzwalacze + potok 9 kroków
├── compute/                    # 7 narzędzi (czysty Python, Skyfield + JPL de421)
│   ├── chart_engine.py         #   karta: pozycje geocentryczne/tropikalne, domy,
│   │                           #   godności wg Lilly'ego + sekta, aspekty z fazami,
│   │                           #   kondycja słoneczna, loty, godziny planetarne
│   ├── synastry.py             #   interaspekty + nakładki domów + dopasowanie
│   ├── composite.py            #   karta kompozytowa (midpointy krótszego łuku)
│   ├── synastry_transits.py    #   tranzyty relacji (3 warstwy)
│   ├── render_chart.py         #   tabele tekstowe 72 kol. (PL/EN)
│   ├── render_html.py          #   HTML: koło SVG, tabele, dymki definicji
│   └── render_html_synastry.py #   HTML synastrii (2–3 koła)
├── resources/                  # baza wiedzy (10 plików: planety, znaki, domy,
│                               #   aspekty, godności, dekany, loty, kompozyt,
│                               #   zasady hermetyczne, godziny planetarne)
└── templates/full-reading.md   # szkielet raportu (geometria 72 kolumn)

output/                         # wyniki (konwencja niżej)
CLAUDE.md                       # przewodnik techniczny dla Claude Code
```

**Zasada podziału:** silnik liczy, model interpretuje. Cała astronomia i punktacja
siedzi w JSON-ach (`chart.json` itd.) — interpretacja zawsze ma pokrycie w liczbach.

## Konwencja wyników

```
output/<zodiak>_<data-ur>/<data-ur>_<data-odczytu>_<metoda>_<cel>/   # indywidualne
output/synastria/<A>_x_<B>_<data-odczytu>_<cel>/                     # pary
```

Każdy folder: `reading.md` (raport 72-kolumnowy) + `reading.html` (koło SVG,
kolorowane godności, siatka aspektów, dymki z definicjami pojęć dla laika)
+ surowe JSON-y. Szczegóły: [`output/README.md`](output/README.md).

## Jakość i rzetelność

- **Astronomia:** Skyfield + JPL de421 — pozycje geocentryczne, ekliptyka daty,
  prawdziwy czas gwiazdowy (GAST), nutacja; domy: Znaki Całe / Equal / Porphyry /
  Placidus. Zweryfikowane **58 testami** (jednostkowe + integracyjne) oraz audytem
  wieloagentowym (37 znalezisk, wszystkie naprawione).
- **Tradycja:** punktacja godności wg Lilly'ego (z peregrinem sumującym się
  z debilitacjami), tryplicytety, terminy egipskie, oblicza chaldejskie, sekta
  z rzeczywistej wysokości Słońca, doby planetarne od wschodu do wschodu.
- **Etyka (wbudowana w skill):** język probabilistyczny, zero fatalizmu i straszenia,
  bez porad medycznych/prawnych/finansowych; każdy odczyt jest samodzielny —
  bez odniesień do odczytów innych osób.

## Wymagania

- Windows / macOS / Linux, Python ≥ 3.10 (testowane na 3.13), `skyfield`
- (opcjonalnie, do PDF) przeglądarka Chromium/Edge w trybie headless

## Eksport / publikacja

Projekt jest gotowy do eksportu (git/zip). **Do paczki nie wchodzą** (patrz
[`.gitignore`](.gitignore)):

- `output/` poza `output/README.md` — odczyty zawierają **prywatne dane
  urodzeniowe realnych osób**;
- `compute/de421.bsp` (~17 MB) — silnik pobiera efemerydę sam przy pierwszym
  uruchomieniu;
- `__pycache__/`, `.claude/settings.local.json`, `export/`.

Gotową paczkę zip składa się do `export/` (nazwa:
`Astrologia_hermetic-astrology_<data>.zip`). Po rozpakowaniu u odbiorcy
wystarczy `py -3.13 -m pip install -r .claude/skills/hermetic-astrology/requirements.txt`.

---

*Astrologia jest tradycją symboliczną — zwierciadłem do refleksji, nie wyrocznią.
„Jak na górze, tak na dole; poznaj samego siebie."*
