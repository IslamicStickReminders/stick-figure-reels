# Offline renderer dependencies

`../setup.sh` creates a local Python environment that can reuse the host's
installed packages. It checks real imports, then uses `../tools/setup_deps.py`
to install missing renderer packages from this bundle before trying PyPI.
It verifies the archive and each wheel against `manifest.json` before
installation. It does not change the host's network or account settings.

The bundled wheels support **CPython 3.11, 3.12 and 3.13 on Linux x86_64
with glibc 2.28 or newer**. They contain:

- [skia-python 144.1](https://pypi.org/project/skia-python/144.1/), with one wheel for each supported Python version.
- [uharfbuzz 0.57.0](https://pypi.org/project/uharfbuzz/0.57.0/), using the CPython 3.11 stable ABI.
- [pybind11 3.1.0](https://pypi.org/project/pybind11/3.1.0/), a dependency declared by skia-python.

For a completely offline setup, **NumPy, SciPy, Pillow, FFmpeg and ffprobe
must already be available**. Skia also requires host system libraries,
including **libGL and libEGL**; this archive does not supply those libraries
or a Python interpreter. Run `STICK_REEL_OFFLINE=1 bash setup.sh` from the
kit folder to prevent setup from trying PyPI. Setup reports failure if
required imports or tools still do not work.

Other Python versions, operating systems and architectures need their own
compatible packages through an available, approved installation route.
These files do not guarantee a particular Claude runtime or enable code
execution when the host has disabled it.

## Provenance and licences

The wheels came from the official PyPI releases linked above. Their original
download URLs and SHA-256 checksums are recorded under `sources` in
`manifest.json`. To keep the download small, the wheels were repacked without
ZIP compression, then compressed together in `wheels.tar.xz`. **Every file
payload, RECORD entry and included licence remains unchanged.** The manifest
also records the repacked wheel checksums and the archive checksum.

Each wheel retains its upstream licence under its `.dist-info/licenses/`
directory. Those upstream terms apply to these dependencies; the course's
code permission and bundled fonts' licences do not replace them. See also
[`../../THIRD-PARTY-NOTICES.md`](../../THIRD-PARTY-NOTICES.md).
