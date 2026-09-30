"""Unit tests for Instagram Reel publishing helper."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock

from instagram_publish import (
    remux_faststart,
    upload_to_supabase,
    create_reel_container,
    wait_for_container,
    publish_reel_container,
    check_account,
    DEFAULT_APP_ID,
    DEFAULT_APP_SECRET,
)


class InstagramPublishTests(unittest.TestCase):
    def test_default_credentials(self):
        self.assertEqual(DEFAULT_APP_ID, "1736345594332140")
        self.assertEqual(DEFAULT_APP_SECRET, "59ae7b5b3662810ec883abb048e6aa94")

    @patch("subprocess.run")
    def test_remux_faststart_invokes_ffmpeg(self, mock_run):
        mock_run.return_value = Mock(returncode=0, stderr="")
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "in.mp4"
            dst = Path(tmpdir) / "out.mp4"
            src.write_bytes(b"mock video")
            res = remux_faststart(src, dst)
            self.assertEqual(res, dst)
            mock_run.assert_called_once()
            cmd = mock_run.call_args[0][0]
            self.assertIn("-movflags", cmd)
            self.assertIn("+faststart", cmd)

    @patch("urllib.request.urlopen")
    def test_upload_to_supabase(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            video = Path(tmpdir) / "test.mp4"
            video.write_bytes(b"video bytes")
            url = upload_to_supabase(video, "https://example.supabase.co", "test-key", "genz-video")
            self.assertTrue(url.startswith("https://example.supabase.co/storage/v1/object/public/genz-video/test-"))
            self.assertTrue(url.endswith(".mp4"))

    @patch("urllib.request.urlopen")
    def test_create_reel_container(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"id": "container_12345"}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        cid = create_reel_container("https://example.com/video.mp4", "Test Caption", "test_token")
        self.assertEqual(cid, "container_12345")

    @patch("time.sleep", return_value=None)
    @patch("urllib.request.urlopen")
    def test_wait_for_container_finished(self, mock_urlopen, mock_sleep):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"status_code": "FINISHED"}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        # Should complete without error
        wait_for_container("container_12345", "test_token", max_wait_sec=10, poll_interval=1)

    @patch("time.sleep", return_value=None)
    @patch("urllib.request.urlopen")
    def test_wait_for_container_error_raises(self, mock_urlopen, mock_sleep):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"status_code": "ERROR"}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        with self.assertRaises(RuntimeError):
            wait_for_container("container_12345", "test_token", max_wait_sec=10, poll_interval=1)

    @patch("urllib.request.urlopen")
    def test_publish_reel_container(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"id": "media_99999"}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        mid = publish_reel_container("container_12345", "test_token")
        self.assertEqual(mid, "media_99999")


if __name__ == "__main__":
    unittest.main()
