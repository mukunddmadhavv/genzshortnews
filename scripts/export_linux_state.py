"""Stage private provider configuration and OpenCode sessions for SSH migration."""
import json
import os
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
target = root / '.secrets/migration'
target.mkdir(mode=0o700, parents=True, exist_ok=True)
local = '/Users/mukundmadhav/genzshortnews'
remote = '/home/mukund/genzshortnews'
config = json.loads((Path.home()/'.config/opencode/opencode.json').read_text())
provider = config['provider']['azure-apim']
# Resolve file-backed provider secrets without emitting their contents.
def resolve(value):
    if isinstance(value, dict):
        return {key:resolve(item) for key,item in value.items()}
    if isinstance(value, list):
        return [resolve(item) for item in value]
    if isinstance(value, str) and value.startswith('{file:') and value.endswith('}'):
        return Path(value[6:-1]).expanduser().read_text().strip()
    return value

provider_config = {'$schema':'https://opencode.ai/config.json',
                  'provider':{'azure-apim':resolve(provider)},'model':'azure-apim/gpt-6-astra'}
path=target/'opencode-provider.json'
path.write_text(json.dumps(provider_config))
path.chmod(0o600)
sessions=json.loads(subprocess.check_output(['opencode','session','list','--format','json'],text=True))
count=0
for session in sessions:
    if session.get('directory') != str(root):
        continue
    raw=target/'export.tmp'
    with raw.open('w') as stream:
        subprocess.run(['opencode','export',session['id']],stdout=stream,stderr=subprocess.DEVNULL,check=True)
    data=json.loads(raw.read_text())
    # Preserve session IDs while rebasing local paths for Linux.
    exported=json.dumps(data,ensure_ascii=False).replace(local,remote)
    path=target/(session['id']+'.json')
    path.write_text(exported)
    path.chmod(0o600)
    count+=1
raw.unlink(missing_ok=True)
print(f'Staged provider configuration and {count} project sessions privately.')
