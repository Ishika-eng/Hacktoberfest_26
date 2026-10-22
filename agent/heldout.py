#!/usr/bin/env python3
"""Fetch the held-out apps (see agent/heldout/README.md) at their pinned commits into heldout/."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent


def git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def fetch(name, spec, dest_root):
    dest = Path(dest_root) / name
    if (dest / ".git").exists() and git("rev-parse", "HEAD", cwd=dest) == spec["commit"]:
        return dest, False
    dest.mkdir(parents=True, exist_ok=True)
    if not (dest / ".git").exists():
        git("init", "-q", cwd=dest)
        git("remote", "add", "origin", spec["repo"], cwd=dest)
    git("fetch", "-q", "--depth", "1", "origin", spec["commit"], cwd=dest)
    git("checkout", "-q", "FETCH_HEAD", cwd=dest)
    if git("rev-parse", "HEAD", cwd=dest) != spec["commit"]:
        sys.exit(f"error: {name} is not at the pinned commit {spec['commit']}")
    return dest, True


def main():
    manifest = json.loads((ROOT / "heldout" / "manifest.json").read_text())
    for name, spec in manifest.items():
        dest, fetched = fetch(name, spec, REPO / "heldout")
        print(f"{name}: {'fetched' if fetched else 'already at'} {spec['commit'][:10]} ({spec['license']}) -> {dest}")


if __name__ == "__main__":
    main()
