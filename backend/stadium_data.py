import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "stadium_state.json"


def load_stadium_state() -> dict:
    """Loads the mock live stadium state. In a real deployment this would
    be replaced by a call to a live operations feed / IoT crowd-sensor API,
    but the decision engine's interface would stay identical."""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)