#!/usr/bin/env python3
"""Reuse working packages; install missing renderer packages offline first."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import sys
import tarfile
import tempfile


KIT = Path(__file__).resolve().parents[1]
OFFLINE = KIT / "offline"
MODULES = {
    "numpy": "numpy",
    "scipy": "scipy",
    "PIL": "pillow",
    "skia": "skia-python",
    "uharfbuzz": "uharfbuzz",
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def missing_imports() -> dict[str, str]:
    missing = {}
    for module, package in MODULES.items():
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import importlib,sys; importlib.import_module(sys.argv[1])", module],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode:
                detail = (result.stderr or result.stdout).strip().splitlines()
                missing[package] = detail[-1] if detail else f"import exited with status {result.returncode}"
        except subprocess.TimeoutExpired:
            missing[package] = "import timed out"
    return missing


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def unpack_verified_wheels(destination: Path) -> set[str]:
    archive = OFFLINE / "wheels.tar.xz"
    manifest_path = OFFLINE / "manifest.json"
    if not archive.exists() and not manifest_path.exists():
        return set()
    if not archive.is_file() or not manifest_path.is_file():
        raise ValueError("The bundled offline archive or its manifest is missing. Download the complete kit again.")
    manifest = json.loads(manifest_path.read_text())
    if not isinstance(manifest, dict):
        raise ValueError("The offline wheel manifest is invalid.")
    expected_archive = manifest.get("archive_sha256", "")
    wheels = manifest.get("wheels")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_archive) or not isinstance(wheels, dict) or not wheels:
        raise ValueError("The offline wheel manifest is invalid.")
    if digest(archive) != expected_archive:
        raise ValueError("The offline wheel archive failed its SHA-256 check. Download the kit again.")
    for name, sha in wheels.items():
        if (not isinstance(name, str) or PurePosixPath(name).name != name
                or not name.endswith(".whl") or "\\" in name
                or not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha)):
            raise ValueError("The offline wheel manifest contains an invalid filename or checksum.")
    with tarfile.open(archive, "r:xz") as bundle:
        members = bundle.getmembers()
        if len(members) != len(wheels) or {member.name for member in members} != set(wheels):
            raise ValueError("The offline archive contents do not match the manifest.")
        if any(not member.isfile() for member in members) or sum(m.size for m in members) > 512 * 1024 * 1024:
            raise ValueError("The offline archive contains an invalid member.")
        for member in members:
            target = destination / member.name
            source = bundle.extractfile(member)
            if source is None:
                raise ValueError(f"Cannot read bundled wheel: {member.name}")
            with source, target.open("wb") as output:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    output.write(block)
            if digest(target) != wheels[member.name]:
                raise ValueError(f"The bundled wheel failed its SHA-256 check: {member.name}")
    return {normalize(name.split("-", 1)[0]) for name in wheels}


def pip_install(packages: list[str], wheel_dir: Path | None = None) -> bool:
    command = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
               "--only-binary=:all:", "--retries", "0", "--timeout", "15"]
    if wheel_dir is not None:
        command += ["--no-index", "--find-links", str(wheel_dir), "--no-deps", "--force-reinstall"]
    else:
        command += ["--index-url", "https://pypi.org/simple"]
    command += packages
    environment = dict(os.environ)
    # Preserve host proxies, but do not inherit unrelated package registries or
    # installation destinations that could escape this local environment.
    environment["PIP_CONFIG_FILE"] = os.devnull
    for option in ("PIP_EXTRA_INDEX_URL", "PIP_FIND_LINKS", "PIP_TARGET", "PIP_PREFIX", "PIP_ROOT", "PIP_USER"):
        environment.pop(option, None)
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=180, env=environment)
    except subprocess.TimeoutExpired:
        print("Package installation timed out.", file=sys.stderr)
        return False
    if result.returncode:
        detail = (result.stderr or result.stdout).strip().splitlines()
        print("\n".join(detail[-8:]), file=sys.stderr)
        return False
    return True


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    if sys.prefix == sys.base_prefix:
        print("Run bash setup.sh from the kit folder so installation stays in the kit's local Python environment.", file=sys.stderr)
        return 1
    missing = missing_imports()
    if not missing:
        print("All renderer packages are already available; no installation needed.")
        return 0
    print(f"Checking dependencies for Python {platform.python_version()} on {platform.system()} {platform.machine()}.")
    print("Missing or unusable: " + ", ".join(missing))
    if importlib.util.find_spec("pip") is None:
        print("This Python environment has no pip. Use a Python environment with pip, then rerun setup.", file=sys.stderr)
        return 1
    try:
        with tempfile.TemporaryDirectory(prefix="stick-reel-wheels-") as temp:
            wheel_dir = Path(temp)
            available = unpack_verified_wheels(wheel_dir)
            if "skia-python" in missing and "pybind11" in available and importlib.util.find_spec("pybind11") is None:
                print("Installing Skia's pybind11 dependency from the verified offline bundle.")
                pip_install(["pybind11"], wheel_dir)
            for package in missing:
                if normalize(package) in available:
                    print(f"Installing {package} from the verified offline bundle.")
                    pip_install([package], wheel_dir)
    except (OSError, ValueError, tarfile.TarError, json.JSONDecodeError) as exc:
        # Never silently bypass corrupt bundled dependencies with a network install.
        print(str(exc), file=sys.stderr)
        return 1
    missing = missing_imports()
    offline_only = os.environ.get("STICK_REEL_OFFLINE", "").lower() in {"1", "true", "yes"}
    if missing and not offline_only:
        print("Attempting package installation for remaining dependencies: " + ", ".join(missing))
        pip_install(list(missing))
        missing = missing_imports()
    if missing:
        print("Setup is not complete. Unavailable dependencies:", file=sys.stderr)
        for package, detail in missing.items():
            print(f"  {package}: {detail}", file=sys.stderr)
        print(f"Runtime: {sys.implementation.name} {platform.python_version()}, {platform.system()} {platform.machine()}.", file=sys.stderr)
        print("Use the install error above to distinguish an unsupported wheel, a missing system library, and blocked package access. "
              "If this environment cannot install the remaining packages, use a compatible Python environment or the host's approved package-install route.", file=sys.stderr)
        return 1
    print("Renderer packages are available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
