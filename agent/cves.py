"""Optional dependency advisory scan using the public OSV database (https://osv.dev).

Opt-in only (`--cve-scan`): it sends the app's Maven dependency coordinates (group:artifact:version,
not source code) to api.osv.dev. Counts are known advisories for the exact versions, not proof
that the app is exploitable.
"""
import json
import tempfile
import urllib.request
from pathlib import Path
import subprocess

OSV_URL = "https://api.osv.dev/v1/querybatch"


def parse_dependency_list(text):
    """`mvn dependency:list` lines -> sorted unique [(group:artifact, version)]."""
    deps = set()
    for line in text.splitlines():
        parts = line.strip().split(":")
        if len(parts) >= 5 and "." in parts[0]:
            version = parts[-2] if len(parts) >= 6 else parts[3]
            deps.add((f"{parts[0]}:{parts[1]}", version))
    return sorted(deps)


def list_dependencies(mvn, app_dir):
    mvn = str(Path(mvn).resolve()) if "/" in mvn else mvn
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "deps.txt"
        p = subprocess.run([mvn, "-q", "-B", "dependency:list", f"-DoutputFile={out}", "-DappendOutput=false"],
                           cwd=app_dir, capture_output=True, text=True)
        if p.returncode != 0 or not out.exists():
            raise RuntimeError("dependency:list failed:\n" + "\n".join((p.stdout + p.stderr).splitlines()[-8:]))
        return parse_dependency_list(out.read_text())


def _post(body):
    req = urllib.request.Request(OSV_URL, json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def query_osv(deps, post=_post, chunk=500):
    """{ 'group:artifact:version': [advisory ids] } for dependencies that have advisories."""
    found = {}
    for i in range(0, len(deps), chunk):
        part = deps[i:i + chunk]
        queries = [{"version": v, "package": {"name": n, "ecosystem": "Maven"}} for n, v in part]
        results = post({"queries": queries}).get("results", [])
        for (name, version), res in zip(part, results, strict=False):
            ids = sorted({v["id"] for v in res.get("vulns", [])})
            if ids:
                found[f"{name}:{version}"] = ids
    return found


def scan(mvn, app_dir, post=_post):
    deps = list_dependencies(mvn, app_dir)
    found = query_osv(deps, post)
    return {"dependencies": len(deps), "advisories": sorted({i for ids in found.values() for i in ids}),
            "affected": found}
