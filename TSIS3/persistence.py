import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = BASE_DIR / "settings.json"
LEADERBOARD_PATH = BASE_DIR / "leaderboard.json"

DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "red",
    "difficulty": "medium",
}

def read_json(path, default_value):
    if not path.exists():
        return default_value

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default_value

def write_json(path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def load_settings():
    settings = read_json(SETTINGS_PATH, DEFAULT_SETTINGS.copy())
    merged = DEFAULT_SETTINGS.copy()
    merged.update(settings)
    return merged

def save_settings(settings):
    write_json(SETTINGS_PATH, settings)

def load_leaderboard():
    leaderboard = read_json(LEADERBOARD_PATH, [])
    if not isinstance(leaderboard, list):
        return []
    return leaderboard

def save_leaderboard(entries):
    write_json(LEADERBOARD_PATH, entries[:10])

def add_leaderboard_entry(entry):
    entries = load_leaderboard()
    entries.append(entry)
    entries.sort(key=lambda item: (item["score"], item["distance"]), reverse=True)
    save_leaderboard(entries[:10])
    return entries[:10]
