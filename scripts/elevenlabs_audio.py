"""ElevenLabs narration, transcription and SFX; credentials loaded from .env."""
import argparse
import base64
import json
import os
from pathlib import Path
from urllib.parse import quote

import httpx
from dotenv import load_dotenv, set_key


def v4_payload(text, voice, language, stability, similarity):
    settings = {"stability": stability}
    if similarity is not None:
        settings["similarity"] = similarity
    return {"inputs": [{"text": text, "voice_id": voice}], "model_id": "eleven_v4",
            "language_code": language, "settings": settings}


def force_alignment(client, checked, audio, text):
    with audio.open("rb") as stream:
        result = checked(client.post("/v1/forced-alignment", data={"text": text},
                         files={"file": (audio.name, stream, "application/octet-stream")})).json()
    chars = result["characters"]
    if not chars:
        raise SystemExit("Forced alignment returned no characters; audio is preserved.")
    return {"alignment": {"characters": [c["text"] for c in chars],
                          "character_start_times_seconds": [c["start"] for c in chars],
                          "character_end_times_seconds": [c["end"] for c in chars]},
            "normalized_alignment": None, "method": "forced-alignment",
            "loss": result.get("loss")}


def main():
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("models")
    sub.add_parser("voices")
    clone = sub.add_parser("clone", help="Create an Instant Voice Clone from your recording")
    clone.add_argument("--audio", type=Path, required=True)
    clone.add_argument("--name", required=True)
    clone.add_argument("--out", type=Path, required=True, help="Save voice ID and verification status as JSON")
    clone.add_argument("--use-as-default", action="store_true")
    tts = sub.add_parser("tts")
    tts.add_argument("--text", type=Path, required=True)
    tts.add_argument("--out", type=Path, required=True)
    tts.add_argument("--voice", help="Override the configured voice for this take")
    tts.add_argument("--model", default=os.getenv("ELEVENLABS_MODEL_ID", "eleven_v4"))
    tts.add_argument("--language", default=os.getenv("ELEVENLABS_LANGUAGE_CODE", "hi"), help="Base language; hi for Hindi-led Hinglish")
    tts.add_argument("--speed", type=float, default=float(os.getenv("ELEVENLABS_SPEED", "1.0")))
    tts.add_argument("--stability", type=float, default=float(os.getenv("ELEVENLABS_STABILITY", "0.5")))
    tts.add_argument("--similarity", type=float, default=os.getenv("ELEVENLABS_SIMILARITY"), help="Voice similarity, where supported by the model")
    tts.add_argument("--style", type=float, default=os.getenv("ELEVENLABS_STYLE"), help="Style exaggeration, where supported by the model")
    tts.add_argument("--speaker-boost", action=argparse.BooleanOptionalAction, default=os.getenv("ELEVENLABS_SPEAKER_BOOST", "false").lower() == "true")
    sfx = sub.add_parser("sfx")
    sfx.add_argument("--prompt", required=True)
    sfx.add_argument("--duration", type=float, default=0.5)
    sfx.add_argument("--out", type=Path, required=True)
    stt = sub.add_parser("transcribe")
    stt.add_argument("--audio", type=Path, required=True)
    stt.add_argument("--language", default="eng")
    stt.add_argument("--out", type=Path, required=True)
    align = sub.add_parser("align", help="Align saved audio to a script without regenerating speech")
    align.add_argument("--audio", type=Path, required=True)
    align.add_argument("--text", type=Path, required=True)
    align.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "tts" and not 0.7 <= args.speed <= 1.2:
        parser.error("Speech speed must be between 0.7 and 1.2.")
    if args.command == "tts":
        for value in (args.stability, args.similarity, args.style):
            if value is not None and not 0 <= value <= 1:
                parser.error("Stability, similarity and style must be between 0 and 1.")
        if args.model == "eleven_v3" and args.stability not in (0, 0.5, 1):
            parser.error("Eleven v3 stability must be 0, 0.5 or 1.")
        if args.model == "eleven_v4" and (args.speed != 1 or args.style not in (None, 0) or args.speaker_boost):
            parser.error("V4 dialogue does not use TTS speed/style/speaker boost; use speed 1, style 0 and --no-speaker-boost.")
    key = (os.getenv("ELEVENLABS_API_KEY") or os.getenv("ELEVEN_LABS_KEY") or "").strip()
    if not key:
        parser.error("Set ELEVENLABS_API_KEY in .env before making API requests.")
    if args.command == "clone" and not args.audio.is_file():
        parser.error("Voice recording does not exist.")
    if args.command in {"tts", "sfx", "transcribe", "clone", "align"}:
        outputs = [args.out]
        if args.command == "tts":
            outputs.append(args.out.with_suffix(".alignment.json"))
            outputs.append(args.out.with_suffix(".generation.json"))
        if any(p.exists() for p in outputs):
            parser.error("Output already exists; choose a new filename to preserve the previous take.")
        if args.command in {"tts", "sfx"} and args.out.suffix.lower() != ".mp3":
            parser.error("Audio output must use .mp3 for the configured output format.")
        args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.command == "sfx" and not 0.5 <= args.duration <= 30:
        parser.error("SFX duration must be between 0.5 and 30 seconds.")

    def checked(response):
        if response.is_error:
            # Do not print request headers, credentials or user-provided text.
            raise SystemExit(f"ElevenLabs HTTP {response.status_code}; check account access, quota and endpoint parameters. No automatic paid retry was attempted.")
        return response

    try:
        with httpx.Client(base_url="https://api.elevenlabs.io", headers={"xi-api-key": key}, timeout=180) as client:
            if args.command in {"models", "voices"}:
                endpoint = "/v1/models" if args.command == "models" else "/v2/voices"
                print(json.dumps(checked(client.get(endpoint)).json(), ensure_ascii=False, indent=2))
                return
            if args.command == "clone":
                with args.audio.open("rb") as audio:
                    response = client.post("/v1/voices/add", data={"name": args.name, "description": "User's own voice, recorded in conversational Hinglish", "remove_background_noise": "false"}, files={"files": (args.audio.name, audio, "application/octet-stream")})
                if response.is_error:
                    try:
                        detail = response.json().get("detail", {})
                        status = detail.get("status", "unknown") if isinstance(detail, dict) else "unknown"
                    except ValueError:
                        status = "unknown"
                    print(f"Voice cloning failed: HTTP {response.status_code}, status={str(status)[:100]}")
                data = checked(response).json()
                data.update({"name": args.name, "source_audio": str(args.audio.resolve()), "previous_voice_id": os.getenv("ELEVENLABS_VOICE_ID", ""), "default_activated": False})
                # Persist the created ID before changing configuration; never retry creation automatically.
                args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
                if data.get("requires_verification", True):
                    print("Clone saved; ElevenLabs requires owner verification before activation.")
                elif args.use_as_default and data.get("voice_id"):
                    set_key(str(Path(__file__).resolve().parents[1] / ".env"), "ELEVENLABS_VOICE_ID", data["voice_id"])
                    data["default_activated"] = True
                    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
                    print(f"Default narration voice set to {data['voice_id']}")
            elif args.command == "tts":
                voice = (args.voice or os.getenv("ELEVENLABS_VOICE_ID", "")).strip()
                if not voice:
                    parser.error("Set ELEVENLABS_VOICE_ID after selecting a voice.")
                text = args.text.read_text().strip()
                if not text:
                    parser.error("Narration text is empty.")
                if args.model == "eleven_v4":
                    if len(text) > 2000:
                        parser.error("Keep v4 dialogue requests within 2,000 characters for reliable generation.")
                    payload = v4_payload(text, voice, args.language, args.stability, args.similarity)
                    response = checked(client.post("/v1/text-to-dialogue", params={"output_format": "mp3_44100_128"}, json=payload))
                    args.out.write_bytes(response.content)
                    args.out.with_suffix(".generation.json").write_text(json.dumps({
                        "endpoint": "/v1/text-to-dialogue", "request": payload,
                        "request_id": response.headers.get("request-id"),
                    }, ensure_ascii=False, indent=2))
                    # Save the paid take before alignment; an alignment failure must not regenerate speech.
                    print(f"Saved v4 audio: {args.out}. Aligning the saved take.")
                    def alignment_checked(response):
                        if response.status_code in (401, 403):
                            try:
                                detail = response.json().get("detail", {})
                            except ValueError:
                                detail = {}
                            if isinstance(detail, dict) and detail.get("status") == "missing_permissions":
                                raise PermissionError("forced-alignment permission unavailable")
                        return checked(response)

                    try:
                        data = force_alignment(client, alignment_checked, args.out, text)
                    except PermissionError:
                        data = {"alignment": None, "normalized_alignment": None,
                                "status": "alignment_permission_required",
                                "note": "Audio preserved. Obtain verified timing before scheduling visuals/SFX."}
                        print("Alignment permission unavailable: continuing audio processing only. Obtain timing before rendering video.")
                    args.out.with_suffix(".alignment.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
                    print(f"Saved {args.out} and alignment status")
                    return
                if args.model == "eleven_v3" and len(text) > 5000:
                    parser.error("Eleven v3 supports at most 5,000 characters per request.")
                settings = {"stability": args.stability, "speed": args.speed}
                if args.similarity is not None:
                    settings["similarity_boost"] = args.similarity
                if args.style is not None:
                    settings["style"] = args.style
                if args.model != "eleven_v3":
                    settings["use_speaker_boost"] = args.speaker_boost
                payload = {"text": text, "model_id": args.model, "voice_settings": settings}
                if args.model != "eleven_multilingual_v2":
                    payload["language_code"] = args.language
                data = checked(client.post(f"/v1/text-to-speech/{quote(voice, safe='')}/with-timestamps", params={"output_format": "mp3_44100_128"}, json=payload)).json()
                audio = base64.b64decode(data.pop("audio_base64"), validate=True)
                args.out.write_bytes(audio)
                args.out.with_suffix(".alignment.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
                if not (data.get("normalized_alignment") or data.get("alignment")):
                    print("Audio saved without alignment; transcribe the final take before captioning.")
            elif args.command == "align":
                data = force_alignment(client, checked, args.audio, args.text.read_text().strip())
                args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
            elif args.command == "sfx":
                response = checked(client.post("/v1/sound-generation", params={"output_format": "mp3_44100_128"}, json={"text": args.prompt, "duration_seconds": args.duration, "model_id": "eleven_text_to_sound_v2", "prompt_influence": 0.3}))
                args.out.write_bytes(response.content)
            else:
                with args.audio.open("rb") as audio:
                    data = checked(client.post("/v1/speech-to-text", data={"model_id": "scribe_v2", "language_code": args.language, "timestamps_granularity": "word", "tag_audio_events": "true"}, files={"file": (args.audio.name, audio, "application/octet-stream")})).json()
                args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
            print(f"Saved {args.out}")
    except httpx.RequestError:
        raise SystemExit("ElevenLabs network request failed. Check connectivity and generation history before retrying a paid request.") from None


if __name__ == "__main__":
    main()
