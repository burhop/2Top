"""Utilities for loading golden digests used by tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent
DIGEST_DIR = BASE_DIR / "digests"


def load_digest(name: str) -> Dict[str, Any]:
    """Load a JSON digest by name (filename without extension)."""

    path = DIGEST_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Golden digest not found: {path}")
    return json.loads(path.read_text())
