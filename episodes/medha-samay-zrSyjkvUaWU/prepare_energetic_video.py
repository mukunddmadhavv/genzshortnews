"""Sync the energetic revision to its retimed alignment."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
plan = json.loads((root / "image-plan.json").read_text())
data = json.loads((root / "narration-mukund-energetic.alignment.json").read_text())
alignment = data.get("normalized_alignment") or data["alignment"]
text = "".join(alignment["characters"])
plan.update({"alignment": "narration-mukund-energetic.alignment.json", "narration": "narration-mukund-energetic.wav", "output": "news-panel-mukund-energetic.mp4", "beats_output": "image-beats-mukund-energetic.json"})
for beat in plan["beats"]:
    if "phrase" in beat:
        position = text.casefold().find(beat["phrase"].casefold())
        if position < 0:
            raise ValueError(beat["phrase"])
        beat["start"] = alignment["character_start_times_seconds"][position]
(root / "image-plan-mukund-energetic.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2))
cues = [{"file": "../../library/sfx/user-whoosh.mp3", "start_seconds": max(0, plan["beats"][i]["start"] - 0.3), "gain_db": -12} for i in (1, 3, 5, 6)]
(root / "sfx-cues-mukund-energetic.json").write_text(json.dumps(cues, indent=2))
