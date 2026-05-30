"""Pytest configuration: make app modules importable.

Tests mix `import backend.X` and `import X` (db, grader, exercises...).
Put both `app/` and `app/backend/` on sys.path so either style resolves.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT / "app" / "backend"))
