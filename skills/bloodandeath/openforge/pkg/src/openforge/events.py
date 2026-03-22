from __future__ import annotations

import json
import subprocess
from contextlib import suppress
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from openforge.schemas.events import ForgeEvent

if TYPE_CHECKING:
    from pathlib import Path


def emit_event(event: ForgeEvent, run_dir: Path) -> None:
    """Write to events.jsonl AND try openclaw system event. Fire-and-forget for openclaw."""
    run_dir.mkdir(parents=True, exist_ok=True)
    events_path = run_dir / "events.jsonl"
    with events_path.open("a", encoding="utf-8") as handle:
        handle.write(event.model_dump_json())
        handle.write("\n")

    with suppress(OSError):
        subprocess.Popen(
            [
                "openclaw", "system", "event",
                "--mode", "now",
                "--text", json.dumps(event.model_dump(mode="json")),
            ],
            cwd=run_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def make_event(event_type: str, run_id: str, **data: object) -> ForgeEvent:
    """Helper to construct a ForgeEvent with timestamp."""
    return ForgeEvent(
        event=event_type,
        run_id=run_id,
        timestamp=datetime.now(UTC).isoformat(),
        data=data,
    )
