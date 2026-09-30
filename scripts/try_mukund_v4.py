"""Generate a v4 audition with the existing Mukund Tight clone."""
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]


def main():
    load_dotenv(ROOT / ".env")
    key = (os.getenv("ELEVENLABS_API_KEY") or os.getenv("ELEVEN_LABS_KEY") or "").strip()
    if not key:
        raise SystemExit("ElevenLabs API key is missing.")
    presets = json.loads((ROOT / "library/voices/presets.json").read_text())
    preset = next(p for p in presets["presets"] if p["id"] == "mukund-tight")
    script = ROOT / "episodes/medha-samay-zrSyjkvUaWU/narration-hinglish.txt"
    out = ROOT / "library/voices/mukund-hinglish/v4-audition"
    out.mkdir(exist_ok=True)
    audio = out / "mukund-tight-v4-raw.mp3"
    if audio.exists():
        raise SystemExit("V4 audio already exists; preserving the previous take.")
    payload = {
        "inputs": [{"text": script.read_text().strip(), "voice_id": preset["voice_id"]}],
        "model_id": "eleven_v4",
        "language_code": "hi",
        "settings": {"stability": 0.5, "similarity": preset["similarity_boost"]},
    }
    record = {
        "preset": "mukund-tight", "source_script": str(script.relative_to(ROOT)),
        "endpoint": "/v1/text-to-dialogue", "request": payload,
        "note": "Existing clone reused. Dialogue settings differ from v2; raw audition has no local tempo or pause processing.",
    }
    (out / "request.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    with httpx.Client(timeout=180) as client:
        response = client.post(
            "https://api.elevenlabs.io/v1/text-to-dialogue",
            headers={"xi-api-key": key}, params={"output_format": "mp3_44100_128"},
            json=payload,
        )
    if response.is_error:
        try:
            detail = response.json().get("detail", {})
        except ValueError:
            detail = "Non-JSON error response"
        safe = json.loads(json.dumps(detail).replace(key, "[REDACTED]"))
        failure = {"http_status": response.status_code, "detail": safe}
        (out / "error.json").write_text(json.dumps(failure, indent=2) + "\n")
        raise SystemExit(json.dumps(failure, indent=2))
    audio.write_bytes(response.content)
    record["request_id"] = response.headers.get("request-id")
    record["content_type"] = response.headers.get("content-type")
    record["bytes"] = len(response.content)
    (out / "generation.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(f"Saved {audio}")


if __name__ == "__main__":
    main()
