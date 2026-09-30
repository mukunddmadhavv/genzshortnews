"""Unit tests for Instagram OAuth & Token Exchange helper."""
import json
import unittest
from unittest.mock import patch, MagicMock

from instagram_auth import (
    get_auth_url,
    exchange_token,
    refresh_token,
    inspect_account,
    DEFAULT_APP_ID,
    DEFAULT_APP_SECRET,
)


class InstagramAuthTests(unittest.TestCase):
    def test_default_credentials(self):
        self.assertEqual(DEFAULT_APP_ID, "1736345594332140")
        self.assertEqual(DEFAULT_APP_SECRET, "59ae7b5b3662810ec883abb048e6aa94")

    def test_auth_url_contains_scopes(self):
        url = get_auth_url("1736345594332140", "https://example.com/callback")
        self.assertIn("client_id=1736345594332140", url)
        self.assertIn("instagram_business_content_publish", url)
        self.assertIn("instagram_business_basic", url)
        self.assertIn("https%3A%2F%2Fexample.com%2Fcallback", url)

    @patch("urllib.request.urlopen")
    def test_exchange_token(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "access_token": "long_lived_token_xyz",
            "token_type": "bearer",
            "expires_in": 5184000
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = exchange_token(DEFAULT_APP_SECRET, "short_token_123")
        self.assertEqual(res["access_token"], "long_lived_token_xyz")
        self.assertEqual(res["expires_in"], 5184000)

    @patch("urllib.request.urlopen")
    def test_refresh_token(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "access_token": "refreshed_token_xyz",
            "token_type": "bearer",
            "expires_in": 5184000
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = refresh_token("existing_token_123")
        self.assertEqual(res["access_token"], "refreshed_token_xyz")

    @patch("urllib.request.urlopen")
    def test_inspect_account(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "id": "17841400000000000",
            "username": "genzshortnews"
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = inspect_account("token_123")
        self.assertEqual(res["username"], "genzshortnews")
        self.assertEqual(res["id"], "17841400000000000")


if __name__ == "__main__":
    unittest.main()
