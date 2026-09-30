"""Read-only ElevenLabs and local media readiness check; never emits credentials."""
from pathlib import Path
import json
import os
import httpx
from dotenv import load_dotenv

root=Path(__file__).resolve().parents[1]
load_dotenv(root/'.env')
key=os.getenv('ELEVENLABS_API_KEY') or os.getenv('ELEVEN_LABS_KEY')
assert key, 'ElevenLabs key missing'
with httpx.Client(base_url='https://api.elevenlabs.io',headers={'xi-api-key':key},timeout=30) as client:
    response=client.get('/v1/voices/F2bjsMJJPYo3S15YpV24')
    print('Approved narrator lookup HTTP:',response.status_code)
    response.raise_for_status()
    response=client.post('/v1/text-to-dialogue',json={
        'inputs':[{'text':'नमस्ते।','voice_id':'F2bjsMJJPYo3S15YpV24'}],
        'model_id':'eleven_v4','language_code':'hi',
        'settings':{'stability':0.5,'similarity_boost':0.9}},timeout=90)
    print('Eleven v4 narration HTTP:',response.status_code)
    if response.status_code!=200:
        try:print('Provider error:',response.json().get('detail',{}).get('status','unknown'))
        except Exception:pass
        raise SystemExit(1)
    (root/'output/linux-narration-check.mp3').write_bytes(response.content)
    print('Narration bytes:',len(response.content))
assert (root/'library/sfx/user-whoosh.mp3').is_file()
print('Gameplay clips:',len(list((root/'library/gameplay').rglob('*.mp4'))))
print('User whoosh: present')
