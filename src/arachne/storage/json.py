"""Simple JSON file storage for snapshots."""

import json
from collections.abc import Sequence
from pathlib import Path


class JsonFileJobStorage:
    def __init__(self, root: Path) -> None:
        self.root = root

    def save(self, source: str, payload: Sequence[object], filename: str = "jobs.json") -> Path:
        target_dir = self.root / source
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / filename
        target_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return target_file

    def save_raw(self, source: str, raw_payload: object) -> Path:
        """Save the raw fetched payload to raw.json for inspection.

        raw_payload may be any JSON-serializable object returned by the fetcher.
        """
        target_dir = self.root / source
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "raw.json"
        target_file.write_text(
            json.dumps(raw_payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return target_file
