#!/usr/bin/env python3
"""Run the isolated balanced-tracker short-strip pitch truth-Kalman study."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis/strixel_pitch_study"))
from truth import main

if __name__ == "__main__":
    main()
