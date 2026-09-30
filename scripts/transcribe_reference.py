"""Local Whisper transcription on Apple Silicon; preserves uncertain ASR output."""
import argparse
import json
import os
from pathlib import Path

import platform

def transcribe(audio, model):
    if platform.system() == 'Darwin' and platform.machine() == 'arm64':
        import mlx_whisper
        return mlx_whisper.transcribe(audio, path_or_hf_repo=model, language='hi', word_timestamps=True, condition_on_previous_text=False)
    from faster_whisper import WhisperModel
    if model.startswith('mlx-community/'):
        model = model.removeprefix('mlx-community/whisper-').removesuffix('-mlx')
    engine = WhisperModel(model, device='cpu', compute_type='int8', cpu_threads=min(8,os.cpu_count() or 4))
    segments, info = engine.transcribe(audio, language='hi', word_timestamps=True, condition_on_previous_text=False)
    output=[]
    for segment in segments:
        output.append({'start':segment.start,'end':segment.end,'text':segment.text,'words':[{'start':w.start,'end':w.end,'word':w.word,'probability':w.probability} for w in segment.words or []]})
    return {'text':''.join(s['text'] for s in output),'language':info.language,'segments':output,'backend':'faster-whisper-cpu-int8','model':model}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("audio")
parser.add_argument("--out", type=Path, required=True)
parser.add_argument("--model", default="mlx-community/whisper-small-mlx")
parser.add_argument("--fallback-model", default="mlx-community/whisper-small-mlx", help="Fallback model if primary model fails")
args = parser.parse_args()
try:
    result = transcribe(args.audio, args.model)
except Exception as e:
    if args.fallback_model and args.fallback_model != args.model:
        print(f"Warning: model {args.model} failed ({e}); falling back to {args.fallback_model}...")
        result = transcribe(args.audio, args.fallback_model)
    else:
        raise
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
for segment in result["segments"]:
    print(f"{segment['start']:.2f}–{segment['end']:.2f}: {segment['text']}")
os._exit(0)

