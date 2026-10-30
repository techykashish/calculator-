"""Local JSON persistence for recent calculations."""

from __future__ import annotations

import json
import os
from pathlib import Path


class HistoryStore:
    """Stores a short calculation history in the user's application data folder."""

    def __init__(self) -> None:
        if os.name == "nt":
            base_directory = Path(
                os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
            )
        else:
            base_directory = Path(
                os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
            )
        self.path = base_directory / "ProCalc" / "history.json"

    def load(self) -> list[dict[str, str]]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as file:
            entries = json.load(file)
        if not isinstance(entries, list):
            raise ValueError("The saved calculation history has an invalid format.")
        return [
            entry
            for entry in entries
            if isinstance(entry, dict)
            and isinstance(entry.get("expression"), str)
            and isinstance(entry.get("result"), str)
        ][:100]

    def save(self, entries: list[dict[str, str]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(entries[:100], file, indent=2)
