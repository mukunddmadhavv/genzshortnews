"""Run the established complete-decode, loudness and phone-frame checks here."""
import importlib.util
from pathlib import Path

EP = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("episode_verifier", EP.parent / "sunil-pal-ez1YRJeIJyw/verify.py")
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)
verifier.EP = EP
verifier.VIDEO = EP / "final-genz-short-news.mp4"

if __name__ == "__main__":
    verifier.main()
