import os
import subprocess
from pathlib import Path


def run_tesseract(input_path: str) -> str:
    tesseract = os.getenv("TESSERACT_PATH", "tesseract")
    in_path = Path(input_path)
    if not in_path.exists():
        raise FileNotFoundError(str(in_path))

    # Use a temp output base in the same folder
    out_base = in_path.with_suffix("")
    cmd = [tesseract, str(in_path), str(out_base)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or "tesseract failed")

    out_txt = out_base.with_suffix(".txt")
    if not out_txt.exists():
        raise RuntimeError("OCR output not found")

    text = out_txt.read_text(encoding="utf-8", errors="ignore")
    return text
