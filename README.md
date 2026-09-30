# Indian Gen-Z news Shorts — reference and workflow

## Web production studio

The Turborepo dashboard runs at **http://localhost:6969** with PostgreSQL-backed
sessions, resumable OpenCode generation, revision previews, episode import and
channel-verified YouTube uploads to **@genzshotnews**.

```sh
npm run build
npm start
# In another terminal, show your local studio password:
npm run access
```

See [dashboard setup and workflow](docs/dashboard.md) for PostgreSQL, Cloudflare
Tunnel, automatic uploads, recovery, storage and tests.

FFmpeg-first, 9:16 news visuals over continuous gameplay, with Hinglish narration
in Mukund's approved Eleven v4 cloned voice and local DSP sound effects.

## Start here

- **Only approved voice: Mukund Tight — Eleven v4**, recipe 3. Expressive Hinglish,
  minimal pauses; fixed 1.07× + 1.10× local tempo stages.
  [Listen to the approved reference](library/voices/mukund-hinglish/v4-audition/mukund-tight-v4.mp3).
  [Full voice recipe](.skills/indian-news-shorts/references/voice-presets.md).
  Machine-readable preset: `library/voices/presets.json`.
  Generate with `scripts/narrate_with_preset.py` to include all processing.

- [Main skill](.skills/indian-news-shorts/SKILL.md)
- [Detailed reference analysis](.skills/indian-news-shorts/references/reference-analysis.md)
- [Every second of the reference](.skills/indian-news-shorts/references/second-by-second.md)
- [Voice, transcript interpretation and ElevenLabs](.skills/indian-news-shorts/references/narration-and-elevenlabs.md)
- [Production and ideation](.skills/indian-news-shorts/references/production-workflow.md)
- [FFmpeg commands](.skills/indian-news-shorts/references/ffmpeg-recipes.md)

## Downloaded reference

`references/neonman/CFZ6qULa8dU.mp4`: 45.12 seconds, 1080×1920, 60 fps.
`frames/`: 46 integer-second full-resolution samples.
`contact-sheets/`: four labeled visual summaries.
`transcript.turbo.json`: approximate Hindi/Hinglish ASR with word timings.
`probe.json` and `measurements.json`: technical evidence.

## Ready now

- Reference analysis and reusable project skill, registered through `opencode.json`.
- Folder-based gameplay library with [15 downloaded clips](library/gameplay/COLLECTION.md).
- ElevenLabs helper for models/voices, narration with alignment, SFX and transcription.
- FFmpeg compositor with original branding, continuous gameplay, narration and timed SFX.

## Production

Credentials are configured locally in `.env`; see `.env.example` for field names.
Eleven v4 generation succeeded with the existing Mukund clone. Use the preset
wrapper to generate future narration with the approved processing chain.
The reference's exact vocal inflections and SFX require direct listening;
ASR is not an acoustic review.
The studio orchestrates generation through the current skill and existing scripts.
It supports manual or automatic uploads after rendering; publishing schedules and
continuous news discovery are not configured.

Quit and restart OpenCode to load the newly registered `.skills/` skill.

## Connect YouTube

Install the OAuth helper dependencies:

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements-youtube.txt
```

Run the helper with your downloaded **Web application** client JSON:

```sh
.venv/bin/python scripts/youtube_oauth.py \
  --client-json /absolute/path/to/client_secret.json \
  --base-url https://u.trypitch.co
```

Point the Cloudflare Tunnel hostname at `http://localhost:6969`, and register
`https://u.trypitch.co/auth/youtube/callback` as a Google OAuth redirect URI.
Open the one-time setup link printed in the terminal and authorize your channel.
For local setup, use `--base-url http://localhost:6969` and register
`http://localhost:6969/auth/youtube/callback` instead. Tokens obtained locally
can also be used by the hosted backend with the same OAuth client.

The helper stores Google authorized-user credentials (including the refresh token)
in `.secrets/youtube-token.json` with owner-only permissions. It never serves files
or displays tokens. Stop it after setup. Existing token files are not overwritten.
Future upload code can load the file with Google's
`google.oauth2.credentials.Credentials.from_authorized_user_file` and refresh it
using `google.auth.transport.requests.Request`.

External OAuth apps in Testing normally issue seven-day refresh tokens for these
scopes. Production status and any required Google verification must be configured
separately. YouTube's API audit for public uploads is also separate.

Run the OAuth checks with:

```sh
.venv/bin/python -m unittest discover -s scripts -p test_youtube_oauth.py
```
