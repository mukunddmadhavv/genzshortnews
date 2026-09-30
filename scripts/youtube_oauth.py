"""One-channel YouTube OAuth setup; credentials never appear in HTTP responses or logs."""
import argparse
import hmac
import json
import os
from pathlib import Path
import secrets
import tempfile
import time
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly"]
CALLBACK = "/auth/youtube/callback"


def load_client(path):
    config = json.loads(path.read_text())
    client = config.get("web", {})
    if not client.get("client_id") or not client.get("client_secret"):
        raise ValueError("Expected a Google Web application OAuth client JSON.")
    if client.get("auth_uri") != "https://accounts.google.com/o/oauth2/auth":
        raise ValueError("Unexpected Google authorization endpoint.")
    if client.get("token_uri") != "https://oauth2.googleapis.com/token":
        raise ValueError("Unexpected Google token endpoint.")
    return config


def save_credentials(path, credentials):
    """Write atomically with owner-only permissions, including on replacement."""
    if not credentials.refresh_token:
        raise ValueError("Google did not return a refresh token; authorize with consent again.")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".youtube-")
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(credentials.to_json())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def make_handler(config, redirect_uri, token_file, setup_key):
    # Import only for serving, so --check works without dependencies.
    from google_auth_oauthlib.flow import Flow

    secure = urlparse(redirect_uri).scheme == "https"
    pending = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Callback URLs contain authorization codes.

        def reply(self, status, body, **headers):
            self.send_response(status)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
            for name, value in headers.items():
                self.send_header(name.replace("_", "-"), value)
            self.end_headers()
            self.wfile.write(body.encode())

        def do_GET(self):
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            if parsed.path == "/healthz":
                return self.reply(200, "YouTube OAuth helper ready")
            if parsed.path == "/auth/youtube/start":
                key = query.get("key", [""])[0]
                if not hmac.compare_digest(key, setup_key):
                    return self.reply(403, "Open the setup link printed in your terminal.")
                if token_file.exists():
                    return self.reply(409, "Token file already exists. Setup will not overwrite it.")
                flow = Flow.from_client_config(config, SCOPES, redirect_uri=redirect_uri,
                                               autogenerate_code_verifier=True)
                url, state = flow.authorization_url(access_type="offline", prompt="consent")
                session = secrets.token_urlsafe(32)
                pending.clear()
                pending.update(flow=flow, state=state, session=session, expires=time.monotonic() + 900)
                cookie = f"youtube_oauth={session}; HttpOnly; SameSite=Lax; Path=/auth/youtube; Max-Age=900"
                if secure:
                    cookie += "; Secure"
                return self.reply(302, "Redirecting to Google", Location=url, Set_Cookie=cookie)
            if parsed.path == CALLBACK:
                cookie = SimpleCookie()
                try:
                    cookie.load(self.headers.get("Cookie", ""))
                    session = cookie["youtube_oauth"].value if "youtube_oauth" in cookie else ""
                except Exception:
                    session = ""
                valid = (bool(pending) and time.monotonic() < pending["expires"]
                         and hmac.compare_digest(query.get("state", [""])[0], pending["state"])
                         and hmac.compare_digest(session, pending["session"]))
                if not valid:
                    return self.reply(400, "Invalid or expired authorization session. Reopen the setup link.")
                flow = pending.pop("flow")
                pending.clear()
                if "error" in query or not query.get("code"):
                    return self.reply(400, "Authorization was not granted. Reopen the setup link to retry.")
                try:
                    flow.fetch_token(code=query["code"][0], timeout=30)
                    credentials = flow.credentials
                    granted = credentials.granted_scopes or credentials.scopes or []
                    if not set(SCOPES).issubset(granted):
                        raise ValueError("Requested YouTube permissions were not granted.")
                    if token_file.exists():
                        raise ValueError("Token file already exists.")
                    save_credentials(token_file, credentials)
                except Exception as exc:
                    # Exception text can include tokens or upstream response bodies.
                    print(f"Authorization failed ({type(exc).__name__}); no credentials displayed.", flush=True)
                    return self.reply(502, "Could not save authorization. Check permissions and retry from the setup link.")
                print(f"YouTube authorization complete. Credentials saved to {token_file}", flush=True)
                return self.reply(303, "Authorization complete", Location="/auth/youtube/done",
                                  Set_Cookie="youtube_oauth=; HttpOnly; SameSite=Lax; Path=/auth/youtube; Max-Age=0")
            if parsed.path == "/auth/youtube/done" and token_file.exists():
                return self.reply(200, "YouTube connected. Tokens are saved on your server. You can close this tab.")
            self.reply(404, "Not found")

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-json", type=Path, required=True)
    parser.add_argument("--base-url", default="https://u.trypitch.co")
    parser.add_argument("--port", type=int, default=6969)
    parser.add_argument("--token-file", type=Path, default=ROOT / ".secrets/youtube-token.json")
    parser.add_argument("--check", action="store_true", help="Show registered redirects without printing secrets")
    args = parser.parse_args()
    try:
        config = load_client(args.client_json)
    except (OSError, ValueError):
        parser.error("Cannot load valid Google Web client credentials from the supplied path.")
    redirects = config["web"].get("redirect_uris", [])
    if args.check:
        print("Valid Web OAuth client. Registered redirect URIs:")
        for uri in redirects:
            print(uri)
        return
    base = args.base_url.rstrip("/")
    parsed = urlparse(base)
    if parsed.scheme != "https" and not (parsed.scheme == "http" and parsed.hostname == "localhost"):
        parser.error("Use HTTPS, or HTTP localhost for local setup.")
    if parsed.path or parsed.query or parsed.fragment or parsed.username:
        parser.error("Base URL must be an origin, without path or credentials.")
    redirect = base + CALLBACK
    if redirect not in redirects:
        parser.error(f"Register this redirect URI in Google and download updated JSON: {redirect}")
    if args.token_file.exists():
        parser.error("Token file already exists; keeping existing authorization.")
    key = secrets.token_urlsafe(32)
    handler = make_handler(config, redirect, args.token_file, key)
    with HTTPServer(("127.0.0.1", args.port), handler) as server:
        print(f"Listening on 127.0.0.1:{args.port}", flush=True)
        print(f"Open: {base}/auth/youtube/start?key={key}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
