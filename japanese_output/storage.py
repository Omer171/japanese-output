"""Load and save the user state as one local JSON file."""

import json
import os
from pathlib import Path

from .state import new_state


def load(path):
    path = Path(path)
    state = new_state()
    if path.exists():
        with path.open(encoding="utf-8") as f:
            state.update(json.load(f))  # keys added in newer versions get defaults
    return state


def save(path, state):
    """Write to a temp file and then replace, so a crash mid-write doesn't corrupt the data."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
