"""Download a reviewed image-source manifest and validate actual image bytes."""
import argparse
import hashlib
import io
import json
import urllib.request
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    sources = json.loads(args.manifest.read_text())
    for source in sources:
        dest = args.manifest.parent / source["file"]
        if not dest.exists():
            request = urllib.request.Request(source["image_url"], headers={"User-Agent": "Mozilla/5.0", "Referer": source["page_url"]})
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
            with Image.open(io.BytesIO(raw)) as image:
                image.verify()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)
        raw = dest.read_bytes()
        with Image.open(dest) as image:
            source["width"], source["height"] = image.size
        source["sha256"] = hashlib.sha256(raw).hexdigest()
        print(f"{source['id']}: {source['width']}x{source['height']} -> {dest}")
    args.manifest.write_text(json.dumps(sources, indent=2))


if __name__ == "__main__":
    main()
