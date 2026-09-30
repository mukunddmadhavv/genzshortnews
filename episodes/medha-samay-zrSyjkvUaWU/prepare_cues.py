import json
from pathlib import Path

root = Path(__file__).resolve().parent
beats = json.loads((root / "image-beats.json").read_text())
cues = [{"file": "../../library/sfx/user-whoosh.mp3", "start_seconds": max(0, beats[i]["start"] - 0.3), "gain_db": -11} for i in (1, 3, 5, 6)]
(root / "sfx-cues.json").write_text(json.dumps(cues, indent=2))
