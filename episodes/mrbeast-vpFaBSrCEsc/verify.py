"""Run the established export checks against this episode."""
import importlib.util
from pathlib import Path

EP = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("export_checks", EP.parent / "sunil-pal-ez1YRJeIJyw/verify.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)
checks.EP = EP
checks.VIDEO = EP / "final-genz-short-news.mp4"

if __name__ == "__main__":
    checks.main()
