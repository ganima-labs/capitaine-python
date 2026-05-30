"""Pytest configuration: make `app/` importable so tests can do `import backend.*`."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "app"))
