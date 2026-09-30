"""Offline integration checks for v4 routing and alignment recovery."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx

import elevenlabs_audio


class V4PipelineTests(unittest.TestCase):
    def run_generation(self, directory, fail_alignment=False):
        folder = Path(directory)
        script = folder / "script.txt"
        script.write_text("नमस्ते। Follow GENZ SHORT NEWS for more!")
        out = folder / "raw.mp3"
        calls = []

        def handle(request):
            calls.append(request)
            if request.url.path == "/v1/text-to-dialogue":
                payload = json.loads(request.content)
                self.assertEqual(payload, {
                    "inputs": [{"text": script.read_text(), "voice_id": "test-clone"}],
                    "model_id": "eleven_v4", "language_code": "hi",
                    "settings": {"stability": 0.5, "similarity": 0.9},
                })
                return httpx.Response(200, content=b"mock-audio", headers={"request-id": "test-request"})
            self.assertEqual(request.url.path, "/v1/forced-alignment")
            self.assertEqual(out.read_bytes(), b"mock-audio")
            if fail_alignment:
                return httpx.Response(401, json={"detail": {"status": "missing_permissions"}})
            return httpx.Response(200, json={"characters": [
                {"text": "न", "start": 0.1, "end": 0.2},
                {"text": "म", "start": 0.2, "end": 0.3},
            ], "words": [], "loss": 0.2})

        client = httpx.Client(base_url="https://api.elevenlabs.io", transport=httpx.MockTransport(handle))
        argv = ["elevenlabs_audio.py", "tts", "--voice", "test-clone", "--model", "eleven_v4",
                "--language", "hi", "--speed", "1", "--stability", "0.5", "--similarity", "0.9",
                "--style", "0", "--no-speaker-boost", "--text", str(script), "--out", str(out)]
        with patch("elevenlabs_audio.load_dotenv"), patch.dict("os.environ", {"ELEVENLABS_API_KEY": "test-key"}), \
                patch("sys.argv", argv), patch("elevenlabs_audio.httpx.Client", return_value=client):
            elevenlabs_audio.main()
        self.assertEqual(len(calls), 2)
        self.assertEqual(out.read_bytes(), b"mock-audio")
        self.assertTrue(out.with_suffix(".generation.json").exists())
        return out

    def test_v4_routing_and_real_character_alignment_conversion(self):
        with tempfile.TemporaryDirectory() as directory:
            out = self.run_generation(directory)
            alignment = json.loads(out.with_suffix(".alignment.json").read_text())
            self.assertEqual(alignment["alignment"]["characters"], ["न", "म"])
            self.assertEqual(alignment["alignment"]["character_start_times_seconds"], [0.1, 0.2])
            self.assertEqual(alignment["alignment"]["character_end_times_seconds"], [0.2, 0.3])

    def test_alignment_failure_preserves_paid_audio_without_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            out = self.run_generation(directory, fail_alignment=True)
            alignment = json.loads(out.with_suffix(".alignment.json").read_text())
            self.assertEqual(alignment["status"], "alignment_permission_required")
            self.assertIsNone(alignment["alignment"])


if __name__ == "__main__":
    unittest.main()
