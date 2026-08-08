# Kompozyt i tranzyty relacji (synastry transits)

## Karta kompozytowa (composite chart)

Kompozyt to karta **samej relacji** — „trzeciego bytu”, który powstaje, gdy dwoje
ludzi tworzy parę. Każdy punkt kompozytu leży **w połowie drogi** (krótszym łukiem)
między odpowiadającymi punktami obu kart: kompozytowe Słońce = środek między
Słońcami, Księżyc = środek między Księżycami itd. Domy: Znaki Całe od kompozytowego
Ascendentu (środek Ascendentów).

- **Kompozytowe Słońce** — tożsamość i cel związku („po co jesteśmy razem”).
- **Kompozytowy Księżyc** — emocjonalny klimat i potrzeby pary.
- **Kompozytowe aspekty** — wewnętrzna mechanika relacji jako całości.
- Kompozyt **nie ma** sekty, godności ani lotów — te należą do jednostek.

Narzędzie: `py -3.13 compute/composite.py chartA.json chartB.json` →
`composite.json` (kształt zgodny z chart.json — koło SVG i paski działają wprost).

## Tranzyty relacji — trzy warstwy

Narzędzie: `py -3.13 compute/synastry_transits.py chartA chartB synastry.json
composite.json --from RRRR-MM-DD --to RRRR-MM-DD` → `transits.json`:

1. **`composite_hits`** — tranzyty do punktów kompozytu: pogoda samego związku
   (np. tranzytowy Saturn □ kompozytowy ASC = próba formy relacji).
2. **`string_activations`** — „struny”: tranzyt (Mars…Pluton) staje na końcu
   ciasnego interaspektu pary (orb ≤3°) i pobudza całe połączenie między kartami
   (np. Mars na Księżycu B aktywuje oś Księżyc A ☍ Księżyc B).
3. **`lunations`** — nowie i pełnie okna z numerem DOMU KOMPOZYTU, w który padają
   (nów w IX kompozytu = nowy wspólny plan/podróż/idea).

## Jak czytać (kolejność wagi)

1. Wolne planety do kompozytowych świateł i ASC/MC (nurty wielomiesięczne).
2. Aktywacje strun — dni, gdy niebo gra na połączeniach między kartami.
3. Lunacje w domach kompozytu — rytm miesięczny pary.
4. Mars/Słońce do kompozytu — dni zapłonu i przeglądu.

Zapis wyników: `output/synastria/<A>_x_<B>_<data>_tranzyt-<okres>/`
(reading.md + reading.html + composite.json + transits.json; PDF na życzenie).
Eksport HTML: `render_html_synastry.py ... --composite composite.json`
(dwa koła osób + koło kompozytu).
