import os
from pathlib import Path

_MODULES_DIR = Path(__file__).resolve().parent
MODELS_DIR = Path(os.getenv("WORKER_MODELS_DIR", _MODULES_DIR / "models"))
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", "media"))
