#!/usr/bin/env python3
"""
Style linter for reading.md prose — counts the anti-slop patterns defined in
resources/style.md and prints warnings when budgets are exceeded.

Usage:  py -3.13 style_check.py path/to/reading.md
Exit 0 always (advisory); prints OK when clean.
"""

import re
import sys

BOX = set("│┌└├╞╔╚║═╪┼┤╡┬┴┐┘╗╝█░")

STOCK_METAPHORS = [
    r"\bmgł[aąęoy]\w*", r"\biskr[aąęoy]\w*", r"\bsilnik\w*",
    r"\bwarsztat\w*", r"\bpracowni\w*", r"\bkuźni\w*", r"\bsad\b|\bsadem\b",
    r"\bdrabin\w*", r"koło zamachowe", r"\bhuśtawk\w*",
    r"wiatr w (plecy|kurs)", r"powietrze .{0,12}dmie", r"zamek bez",
]


def prose_lines(text):
    for ln in text.splitlines():
        s = ln.strip()
        if not s or s[0] in BOX or set(s) <= {"─"}:
            continue
        yield ln


def main():
    if len(sys.argv) != 2:
        print("usage: style_check.py reading.md")
        return
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    text = open(sys.argv[1], encoding="utf-8").read()
    prose = " ".join(prose_lines(text))
    warn = []

    contrasts = re.findall(
        r"\bnie [^,.;]{2,40}, (?:lecz|tylko|a) ", prose, re.I)
    if len(contrasts) > 1:
        warn.append(f"kontrast 'nie X, lecz Y': {len(contrasts)}× (budżet 1)")

    triads = re.findall(
        r"\b\w+[^,.;()]{0,20}, \w+[^,.;()]{0,20} i \w+", prose)
    if len(triads) > 2:
        warn.append(f"trójki 'A, B i C': {len(triads)}× (budżet 2)")

    wow = re.findall(r"co do (minuty|ćwierci|pół stopnia)", prose, re.I)
    if len(wow) > 1:
        warn.append(f"'co do minuty…': {len(wow)}× (budżet 1)")

    bangs = re.findall(r"°!|\d!\s", text)
    if len(bangs) > 1:
        warn.append(f"wykrzykniki przy stopniach: {len(bangs)}× (budżet 1)")

    scare = re.findall(r"„(ja|my|u siebie|nas|chcę)”", prose)
    if len(scare) > 3:
        warn.append(f"cudzysłowy ironiczne: {len(scare)}× (budżet 3)")

    for pat in STOCK_METAPHORS:
        hits = re.findall(pat, prose, re.I)
        if hits:
            warn.append(f"dyżurna metafora {pat!r}: {len(hits)}×")

    sents = [s.strip() for s in re.split(r"[.!?]\s", prose) if s.strip()]
    words = [len(s.split()) for s in sents]
    if words and min(words) > 5:
        warn.append("brak zdania ≤5 słów (rytm zbyt równy)")
    dashes = [s for s in sents if s.count("—") > 1]
    if len(dashes) > 3:
        warn.append(f"zdania z >1 myślnikiem: {len(dashes)} (rozbić rytm)")

    if warn:
        print(f"style_check: {len(warn)} ostrzeżeń")
        for w in warn:
            print("  ⚠", w)
    else:
        print("style_check: OK")


if __name__ == "__main__":
    main()
