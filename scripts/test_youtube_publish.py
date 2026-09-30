"""Validate channel guard and upload reconciliation without contacting YouTube."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from youtube_publish import connect, upload


class PublishTests(unittest.TestCase):
    def test_wrong_channel_rejected(self):
        client = Mock()
        client.get.return_value.json.return_value = {"items": [{"id": "wrong", "snippet": {"customUrl": "@trypitch"}}]}
        with patch("youtube_publish.Credentials"), patch("youtube_publish.AuthorizedSession", return_value=client):
            with self.assertRaisesRegex(ValueError, "do not belong"):
                connect(Path("unused.json"))
        client.post.assert_not_called()

    def test_completed_upload_reconciles_without_duplicate_insert(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "video.mp4"
            file.write_bytes(b"fixture")
            checkpoint = Path(directory) / "checkpoint.json"
            checkpoint.write_text(json.dumps({"uri": "https://upload.example/session", "size": 7, "file": str(file)}))
            session = Mock()
            session.put.return_value.status_code = 200
            session.put.return_value.json.return_value = {"id": "existing-video", "status": {"privacyStatus": "private"}}
            result = upload(session, {"id": "right-channel"}, {"file": str(file), "privacy": "public"}, checkpoint)
            self.assertEqual(result["youtube_id"], "existing-video")
            self.assertEqual(result["privacy"], "private")
            session.post.assert_not_called()
            self.assertEqual(checkpoint.stat().st_mode & 0o777, 0o600)

    def test_expired_upload_does_not_create_another(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "video.mp4"
            file.write_bytes(b"fixture")
            checkpoint = Path(directory) / "checkpoint.json"
            checkpoint.write_text(json.dumps({"uri": "https://upload.example/session", "size": 7, "file": str(file)}))
            session = Mock()
            session.put.return_value.status_code = 404
            with self.assertRaisesRegex(ValueError, "expired"):
                upload(session, {"id": "right-channel"}, {"file": str(file), "privacy": "private"}, checkpoint)
            session.post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
