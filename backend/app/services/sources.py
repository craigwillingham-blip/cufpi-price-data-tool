import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = ROOT / "config" / "sources.json"


def load_sources():
    if not CONFIG_PATH.exists():
        return {"sources": []}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def save_sources(payload: dict):
    CONFIG_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
