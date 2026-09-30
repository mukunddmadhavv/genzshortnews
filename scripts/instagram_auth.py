"""Instagram OAuth & Token Exchange helper using Instagram Graph API."""
import argparse
import json
import os
from pathlib import Path
import sys
import urllib.parse
import urllib.request
import urllib.error

DEFAULT_APP_ID = "1736345594332140"
DEFAULT_APP_SECRET = "59ae7b5b3662810ec883abb048e6aa94"
GRAPH_BASE = "https://graph.instagram.com"


def emit(**data):
    print(json.dumps(data), flush=True)


def load_env():
    for name in [".env", ".env.dashboard"]:
        path = Path(name)
        if path.exists():
            for line in path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and not os.environ.get(k):
                        os.environ[k] = v


def get_auth_url(app_id: str, redirect_uri: str) -> str:
    """Return Instagram OAuth authorization URL with required scopes for Reels & Publishing."""
    scopes = [
        "instagram_business_basic",
        "instagram_business_content_publish",
        "instagram_business_manage_comments",
        "instagram_business_manage_messages"
    ]
    params = {
        "client_id": app_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": ",".join(scopes),
        "enable_fb_login": "0",
        "force_authentication": "1"
    }
    return f"https://api.instagram.com/oauth/authorize?{urllib.parse.urlencode(params)}"


def exchange_token(app_secret: str, short_token: str) -> dict:
    """Exchange a short-lived Instagram token for a 60-day long-lived token."""
    url = f"{GRAPH_BASE}/access_token?" + urllib.parse.urlencode({
        "grant_type": "ig_exchange_token",
        "client_secret": app_secret,
        "access_token": short_token
    })
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Token exchange failed ({e.code}): {body}")


def refresh_token(long_token: str) -> dict:
    """Refresh an unexpired long-lived access token for another 60 days."""
    url = f"{GRAPH_BASE}/refresh_access_token?" + urllib.parse.urlencode({
        "grant_type": "ig_refresh_token",
        "access_token": long_token
    })
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Token refresh failed ({e.code}): {body}")


def inspect_account(token: str) -> dict:
    """Inspect account metadata for the authenticated user."""
    url = f"{GRAPH_BASE}/me?fields=id,username,account_type&access_token={urllib.parse.quote(token)}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Account check failed ({e.code}): {body}")


def main():
    load_env()
    parser = argparse.ArgumentParser(description="Instagram Graph API OAuth & Token Management")
    parser.add_argument("--app-id", default=os.environ.get("INSTAGRAM_APP_ID", DEFAULT_APP_ID))
    parser.add_argument("--app-secret", default=os.environ.get("INSTAGRAM_APP_SECRET", DEFAULT_APP_SECRET))
    parser.add_argument("--auth-url", action="store_true", help="Print authorization URL")
    parser.add_argument("--redirect-uri", default="https://u.trypitch.co/auth/instagram/callback")
    parser.add_argument("--exchange", metavar="SHORT_TOKEN", help="Exchange short-lived token for long-lived token")
    parser.add_argument("--refresh", metavar="LONG_TOKEN", help="Refresh existing long-lived token")
    parser.add_argument("--inspect", metavar="TOKEN", help="Inspect account details for token")
    args = parser.parse_args()

    if args.auth_url:
        url = get_auth_url(args.app_id, args.redirect_uri)
        emit(type="auth_url", url=url)
        print(f"\nInstagram OAuth URL:\n{url}")
        return

    if args.exchange:
        result = exchange_token(args.app_secret, args.exchange)
        emit(type="exchanged", **result)
        return

    if args.refresh:
        result = refresh_token(args.refresh)
        emit(type="refreshed", **result)
        return

    if args.inspect:
        result = inspect_account(args.inspect)
        emit(type="inspected", **result)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
