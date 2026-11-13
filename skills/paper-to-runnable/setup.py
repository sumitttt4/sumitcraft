#!/usr/bin/env python3
"""Cross-platform, opt-in setup for the paper-to-runnable skill: a private virtual environment next to this file.

    python setup.py                 show the plan (what would be installed, where, roughly how big). Changes nothing.
    python setup.py --yes           create .venv and install the core packages
    python setup.py --yes --extra NAME   also install an extra (see the plan for the names)

Windows: use `py setup.py` (or setup.ps1). macOS/Linux: `python3 setup.py` (or setup.sh).
It only ever writes inside this skill's .venv folder. It never uses sudo, never changes PATH, never installs
system packages, and never downloads speech models: those download on first use, and the plan says how big.
uv is used if it is on the PATH, otherwise python -m venv + pip.
"""
import os, platform, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENV = HERE / ".venv"
VPY = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
APPLE_SILICON = sys.platform == "darwin" and platform.machine() == "arm64"

# ---- per-skill package plan (edited per skill) ----
CORE = ["numpy", "matplotlib", "pypdf"]
EXTRAS = {"torch": {"packages": ["torch"], "why": "only when hand-written backprop would be longer than the idea itself; CPU wheels are several hundred MB"}}
NOTES = ["fetch_paper.py downloads from arXiv only, and only the paper you name."]


def plan(extras):
    pk = list(CORE)
    for e in extras:
        if e not in EXTRAS:
            sys.exit(f"unknown extra {e!r}; choose from: {', '.join(EXTRAS) or 'none'}")
        pk += EXTRAS[e]["packages"]
    return pk


def main():
    a = sys.argv[1:]
    extras = [a[i + 1] for i, x in enumerate(a) if x == "--extra" and i + 1 < len(a)]
    pk = plan(extras)
    print(f"paper-to-runnable setup plan")
    print(f"  python: {sys.version.split()[0]} ({sys.executable})")
    print(f"  venv:   {VENV} ({'exists' if VPY.exists() else 'will be created'})")
    print(f"  install: {' '.join(pk) or '(nothing)'}")
    for name, e in EXTRAS.items():
        print(f"  extra '{name}': {' '.join(e['packages'])}  -- {e['why']}")
    for n in NOTES:
        print(f"  note: {n}")
    ff = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    print(f"  ffmpeg: {ff or 'NOT FOUND (install it yourself, or set FFMPEG to its full path)'}")
    if "--yes" not in a:
        print("\nNothing changed. Re-run with --yes to create the venv and install the packages above.")
        return
    if sys.version_info < (3, 9):
        sys.exit("Python 3.9 or newer is needed.")
    uv = shutil.which("uv")
    if not VPY.exists():
        subprocess.run([uv, "venv", "-q", str(VENV)] if uv else [sys.executable, "-m", "venv", str(VENV)], check=True)
    if pk:
        cmd = [uv, "pip", "install", "-q", "--python", str(VPY)] if uv else [str(VPY), "-m", "pip", "install", "-q"]
        subprocess.run(cmd + pk, check=True)
    ok = subprocess.run([str(VPY), "-c", "import sys; print(sys.version.split()[0])"], capture_output=True, text=True)
    if ok.returncode != 0:
        sys.exit("the venv was created but its Python does not start; delete .venv and try again")
    print(f"ready: {VPY}")
    if not ff:
        print("ffmpeg is still missing: the scripts that read or write audio and video will stop with an error until it is installed.")


if __name__ == "__main__":
    main()
