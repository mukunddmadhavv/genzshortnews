"""Exercise OAuth session validation and private token persistence without Google calls."""
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
from http.server import HTTPServer

import requests

from youtube_oauth import make_handler, save_credentials


class OAuthTests(unittest.TestCase):
    def test_callback_requires_browser_session_and_stores_tokens(self):
        with tempfile.TemporaryDirectory() as directory:
            token_file = Path(directory) / "private/token.json"
            credentials = Mock(refresh_token="fake-refresh", granted_scopes=[
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.readonly"])
            credentials.to_json.return_value = json.dumps({"refresh_token": "fake-refresh"})
            flow = Mock(credentials=credentials)
            flow.authorization_url.return_value = ("https://accounts.google.com/test", "expected-state")
            with patch("google_auth_oauthlib.flow.Flow.from_client_config", return_value=flow):
                server = HTTPServer(("127.0.0.1", 0), make_handler(
                    {}, "http://localhost/auth/youtube/callback", token_file, "setup-key"))
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                base = f"http://127.0.0.1:{server.server_port}"
                try:
                    browser = requests.Session()
                    self.assertEqual(browser.get(base + "/auth/youtube/start").status_code, 403)
                    start = browser.get(base + "/auth/youtube/start?key=setup-key", allow_redirects=False)
                    self.assertEqual(start.status_code, 302)
                    callback = base + "/auth/youtube/callback?state=expected-state&code=fake-code"
                    self.assertEqual(requests.get(callback).status_code, 400)
                    self.assertEqual(browser.get(callback.replace("expected-state", "wrong")).status_code, 400)
                    flow.fetch_token.assert_not_called()
                    result = browser.get(callback, allow_redirects=False)
                    self.assertEqual(result.status_code, 303)
                    self.assertNotIn("fake-refresh", result.text)
                    flow.fetch_token.assert_called_once_with(code="fake-code", timeout=30)
                    self.assertEqual(token_file.stat().st_mode & 0o777, 0o600)
                    self.assertEqual(token_file.parent.stat().st_mode & 0o777, 0o700)
                    self.assertEqual(browser.get(callback).status_code, 400)
                    self.assertEqual(browser.get(base + "/auth/youtube/start?key=setup-key").status_code, 409)
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join()

    def test_missing_refresh_token_does_not_write_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "token.json"
            with self.assertRaises(ValueError):
                save_credentials(path, Mock(refresh_token=None))
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
