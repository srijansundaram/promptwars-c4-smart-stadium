import json
from pathlib import Path
from functools import lru_cache

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "stadium_state.json"


@lru_cache(maxsize=1)
def load_stadium_state() -> dict:
    """Loads and caches the mock live stadium state. Cached since this is
    static demo data — in a real deployment with a live feed, this would
    be replaced with a short-TTL cache instead of permanent caching."""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)