#!/usr/bin/env python3
from pathlib import Path
import runpy
import sys

target = Path(__file__).resolve().parents[2] / "_xiaogu-runtime" / "scripts" / "validate_artifact.py"
sys.argv.insert(1, "review")
runpy.run_path(str(target), run_name="__main__")
