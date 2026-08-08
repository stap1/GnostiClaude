#!/usr/bin/env bash
# Hermetic Astrology — Compute Mode installer (Skyfield backend)
set -e
DIR="$(dirname "$0")"
echo "Installing Hermetic Astrology compute dependencies (skyfield)..."
# Windows: prefer the py launcher (e.g. 3.13). Fall back to python/python3.
if command -v py >/dev/null 2>&1; then
  py -3.13 -m pip install -r "$DIR/requirements.txt" || py -m pip install -r "$DIR/requirements.txt"
else
  python -m pip install -r "$DIR/requirements.txt" || python3 -m pip install -r "$DIR/requirements.txt"
fi
echo
echo "Done. Test with:"
echo '  py -3.13 compute/chart_engine.py --dob 1993-06-14 --tob 15:40 --lat 54.35 --lon 18.65 --tz 2'
echo
echo "First run downloads de421.bsp (~17 MB) into compute/. If Python is unavailable,"
echo "the skill runs in Prompt Mode automatically."
