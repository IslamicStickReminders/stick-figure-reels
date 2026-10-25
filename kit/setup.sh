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
    python3 -m venv "$venv_dir"
fi
"$venv_dir/bin/python" -m pip install --disable-pip-version-check skia-python numpy scipy pillow uharfbuzz
mkdir -p out test
"$venv_dir/bin/python" -c "import skia, numpy, scipy, PIL, uharfbuzz; print('deps ok')"
ffmpeg -version
echo "Setup complete. Activate the environment before running the examples:"
echo "source $venv_dir/bin/activate"
