"""Retime this episode to the approved Mukund Tight take."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
plan = json.loads((ROOT / "image-plan.json").read_text())
data = json.loads((ROOT / "narration-mukund-tight.alignment.json").read_text())
alignment = data.get("normalized_alignment") or data["alignment"]
text = "".join(alignment["characters"])
plan.update({
    "alignment": "narration-mukund-tight.alignment.json",
    "narration": "narration-mukund-tight.wav",
    "output": "news-panel-mukund-tight.mp4",
    "beats_output": "image-beats-mukund-tight.json",
})
for beat in plan["beats"]:
    if "phrase" in beat:
        position = text.casefold().find(beat["phrase"].casefold())
        if position < 0:
            raise ValueError(f"Missing phrase: {beat['phrase']}")
        beat["start"] = alignment["character_start_times_seconds"][position]
cues = [{"file": "../../library/sfx/user-whoosh.mp3", "start_seconds": max(0, plan["beats"][i]["start"] - 0.3), "gain_db": -11} for i in (1, 3, 5, 6)]
(ROOT / "image-plan-mukund-tight.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2))
(ROOT / "sfx-cues-mukund-tight.json").write_text(json.dumps(cues, indent=2))
print("Retimed eight image beats and four whooshes to Mukund Tight.")
