#!/bin/bash
# One-time setup for the stick-reel kit. Run from the kit folder: bash setup.sh
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

for tool in ffmpeg ffprobe; do
    if ! command -v "$tool" >/dev/null; then
        echo "$tool is missing. Install FFmpeg with your system package manager, then rerun this script." >&2
        exit 1
    fi
done

venv_dir="${STICK_REEL_VENV:-.venv}"
if [[ ! -x "$venv_dir/bin/python" ]]; then
    python3 -m venv --system-site-packages "$venv_dir"
fi
# Reuse packages already supplied by the host, including environments created
# by an earlier version of this kit. Installs still go into this local venv.
"$venv_dir/bin/python" - "$venv_dir/pyvenv.cfg" <<'PY'
from pathlib import Path
import sys
cfg = Path(sys.argv[1])
if not cfg.is_file():
    raise SystemExit("The selected environment has no pyvenv.cfg. Choose a Python venv with STICK_REEL_VENV.")
lines = cfg.read_text().splitlines()
lines = [line for line in lines if not line.lower().startswith("include-system-site-packages")]
lines.append("include-system-site-packages = true")
cfg.write_text("\n".join(lines) + "\n")
PY
"$venv_dir/bin/python" tools/setup_deps.py
mkdir -p out test
"$venv_dir/bin/python" -c "import skia, numpy, scipy, PIL, uharfbuzz; print('deps ok')"
ffmpeg -version
echo "Setup complete. Activate the environment before running the examples:"
printf 'source %q/bin/activate\n' "$venv_dir"
