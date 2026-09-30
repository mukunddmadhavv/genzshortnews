"""Configure the migrated studio on the mukund Linux host without printing secrets."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import time

root=Path('/home/mukund/genzshortnews')
os.chdir(root)
private=root/'.secrets'
private.chmod(0o700)
for item in private.rglob('*'):
    if item.is_file(): item.chmod(0o600)
envfile=private/'postgres.env'
if not envfile.exists():
    envfile.write_text(f'POSTGRES_USER=genz\nPOSTGRES_DB=genz_studio\nPOSTGRES_PASSWORD={secrets.token_hex(24)}\n')
    envfile.chmod(0o600)
db=dict(line.split('=',1) for line in envfile.read_text().splitlines())
exists=subprocess.run(['docker','inspect','genz-studio-postgres'],capture_output=True).returncode==0
if not exists:
    subprocess.run(['docker','run','-d','--name','genz-studio-postgres','--restart','unless-stopped','--env-file',str(envfile),'-p','127.0.0.1:55432:5432','-v','genz-studio-postgres:/var/lib/postgresql/data','postgres:17-alpine'],check=True)
for _ in range(60):
    if subprocess.run(['docker','exec','genz-studio-postgres','pg_isready','-U','genz'],capture_output=True).returncode==0: break
    time.sleep(2)
marker=private/'migration/restored'
if not marker.exists():
    with (private/'migration/genz_studio.dump').open('rb') as stream:
        subprocess.run(['docker','exec','-i','genz-studio-postgres','pg_restore','-U','genz','-d','genz_studio','--no-owner','--no-privileges'],stdin=stream,check=True)
    marker.touch()
config=root/'.env.dashboard'
config.write_text('\n'.join([
    f"DATABASE_URL=postgresql://genz:{db['POSTGRES_PASSWORD']}@127.0.0.1:55432/genz_studio",
    'PORT=6969','HOST=127.0.0.1','DASHBOARD_ORIGIN=https://u.trypitch.co',
    'OPENCODE_CONFIG=/home/mukund/genzshortnews/.secrets/migration/opencode-provider.json',
    'OPENCODE_BIN=/home/mukund/.local/bin/opencode','YOUTUBE_PYTHON=/home/mukund/genzshortnews/.venv/bin/python',
    'YOUTUBE_TOKEN_FILE=/home/mukund/genzshortnews/.secrets/youtube-genzshotnews-token.json','']) )
config.chmod(0o600)
# Rebase copied episode manifests, plans and upload checkpoint paths.
count=0
for base in ['episodes','references','library','data','.secrets/uploads']:
    directory=root/base
    if not directory.exists():continue
    for file in directory.rglob('*'):
        if file.is_file() and file.suffix in {'.json','.txt','.md','.py'}:
            text=file.read_text(errors='replace')
            updated=text.replace('/Users/mukundmadhav/genzshortnews',str(root))
            if text!=updated:file.write_text(updated);count+=1
environment={**os.environ,'OPENCODE_CONFIG':str(private/'migration/opencode-provider.json')}
for file in sorted((private/'migration').glob('ses_*.json')):
    subprocess.run(['opencode','import',str(file)],env=environment,stdout=subprocess.DEVNULL,check=True)
print(f'Imported OpenCode sessions; rebased {count} files.')
subprocess.run(['npm','run','build'],check=True,env=environment)
subprocess.run(['npm','run','db:migrate'],check=True,env=environment)
units=Path.home()/'.config/systemd/user'
common=f'''[Unit]
Description=GENZ News Studio
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory={root}
Environment="PATH={root}/.venv/bin:/home/mukund/.local/bin:/usr/local/bin:/usr/bin:/bin"
Environment="OPENCODE_CONFIG={private}/migration/opencode-provider.json"
ExecStart=/home/mukund/.local/bin/node {root}/apps/server/src/index.js
Restart=on-failure
RestartSec=5
TimeoutStopSec=30
KillMode=control-group
UMask=0077

[Install]
WantedBy=default.target
'''
(units/'genz-studio.service').write_text(common)
bridge=common.replace('Description=GENZ News Studio','Description=Existing tunnel origin bridge to GENZ Studio').replace(f'{root}/apps/server/src/index.js',f'{root}/scripts/tunnel_origin_bridge.mjs')
(units/'genz-origin-bridge.service').write_text(bridge)
subprocess.run(['systemctl','--user','daemon-reload'],check=True)
subprocess.run(['systemctl','--user','enable','--now','genz-studio.service'],check=True)
print('Studio service started on port 6969. Existing service switch remains a separate step.')
