import sys
import pathlib

# Resolve repo root (one level above the tests/ folder)
ROOT = pathlib.Path(__file__).resolve().parents[1]

# Insert only if not already in sys.path
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

