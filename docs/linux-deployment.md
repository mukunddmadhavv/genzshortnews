# Linux deployment — ssh mukund

- Host: `ssh mukund` (Ubuntu x86_64)
- Workspace: `/home/mukund/genzshortnews`
- Studio: `127.0.0.1:6969`, public URL `https://u.trypitch.co`
- Login: configured with `DASHBOARD_PASSWORD` in the copied `.env`
- Runtime configuration: `.env.dashboard`
- Database: Docker `genz-studio-postgres`, PostgreSQL 17, loopback port 55432,
  persistent volume `genz-studio-postgres`
- Service: user-systemd `genz-studio.service`, enabled at boot via user lingering
- Existing tunnel: unchanged. It targets port 2021, so
  `genz-origin-bridge.service` forwards that local port to 6969.
- Replaced services: `richard-dashboard.service` and `richard-worker.service`
  stopped and disabled; the original `/home/mukund/youtube` files are retained.

## Operations

```sh
ssh mukund 'systemctl --user status genz-studio genz-origin-bridge --no-pager'
ssh mukund 'journalctl --user -u genz-studio -n 80 --no-pager'
ssh mukund 'systemctl --user restart genz-studio'
```

The deployed Python environment includes FFmpeg-related Python dependencies,
ElevenLabs/YouTube clients, yt-dlp, uv and faster-whisper. On Linux the ASR helper
uses CPU/int8 faster-whisper rather than Apple MLX; the small model is cached and
was verified against a real episode. Historical Mac paths in media manifests and
the migrated OpenCode transcripts were rebased to the Linux root.

The original OpenCode project conversations were exported/imported with their
session IDs preserved. The service loads the private provider configuration via
`OPENCODE_CONFIG`. It is kept in `.secrets/migration/opencode-provider.json`.
Do not delete that configuration while the service uses it.

The initial migration restored the local PostgreSQL database and copied media,
`.env`, YouTube credentials, branding, scripts and skills. Native Mac node_modules
and virtualenv were excluded and rebuilt for Linux. Local and remote copies do
not synchronize automatically; use the remote dashboard as the active workspace.
