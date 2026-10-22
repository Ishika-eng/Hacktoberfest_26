"""Security equivalence check: ask two builds of the same app the same HTTP questions as
anonymous / user / admin and report every endpoint whose status code differs.

The endpoint list is declared per app in an `endpoints.json` file:

    {"users": {"anonymous": null, "user": ["alice", "alice123"], "admin": ["admin", "admin123"]},
     "endpoints": [{"method": "GET", "path": "/admin/secret"},
                   {"method": "POST", "path": "/orders", "json": {"item": "book", "quantity": 1}}]}
"""
import base64
import http.client
import json
import os
import signal
import socket
import subprocess
import tempfile
import time
import urllib.parse
from pathlib import Path


def load_spec(path):
    return json.loads(Path(path).read_text())


def probe(port, spec, host="127.0.0.1", timeout=10):
    """{(method, path, role): status} for every endpoint and role in the spec."""
    results = {}
    for role, cred in spec["users"].items():
        headers = {}
        if cred:
            token = base64.b64encode(f"{cred[0]}:{cred[1]}".encode()).decode()
            headers["Authorization"] = "Basic " + token
        for ep in spec["endpoints"]:
            h, body = dict(headers), None
            if "json" in ep:
                body, h["Content-Type"] = json.dumps(ep["json"]), "application/json"
            elif "form" in ep:
                body = urllib.parse.urlencode(ep["form"])
                h["Content-Type"] = "application/x-www-form-urlencoded"
            conn = http.client.HTTPConnection(host, port, timeout=timeout)
            try:
                conn.request(ep.get("method", "GET"), ep["path"], body=body, headers=h)
                status = conn.getresponse().status
            except OSError:
                status = "ERR"
            finally:
                conn.close()
            results[(ep.get("method", "GET"), ep["path"], role)] = status
    return results


def compare(before, after):
    """Rows (key, before, after) in a stable order, and the subset whose status differs."""
    rows = [(k, before.get(k), after.get(k)) for k in sorted(set(before) | set(after))]
    return rows, [r for r in rows if r[1] != r[2]]


def category(status):
    """What a status code means for access: allowed, denied, not found, rejected, server error or unreachable."""
    if status == "ERR" or status is None:
        return "unreachable"
    code = int(status)
    if 200 <= code < 400:
        return "allowed"
    if code in (401, 403):
        return "denied"
    if code in (404, 410):
        return "not found"
    if 400 <= code < 500:
        return "rejected"  # reached the app, request refused (400, 405, 415 ...)
    return "server error"


MEANING = {
    ("allowed", "denied"): "access removed (clients that worked now get refused)",
    ("allowed", "not found"): "the route no longer matches; not an access-control change, but clients will break",
    ("allowed", "rejected"): "the request is now refused by the app",
    ("allowed", "server error"): "now fails with a server error",
}


def describe(before, after):
    """(kind, text): kind is 'exposure' when something became accessible, else 'behaviour'."""
    b, a = category(before), category(after)
    if a == "allowed" and b != "allowed":
        return "exposure", f"NEWLY ACCESSIBLE ({b} -> allowed): possible exposure, review first"
    if b == a:
        return "behaviour", f"still {b}, different status"
    return "behaviour", MEANING.get((b, a), f"{b} -> {a}")


def format_differences(diffs):
    """Markdown table of the changed answers, possible exposures first, saying what each change means."""
    rows = []
    for (method, path, role), before, after in diffs:
        kind, text = describe(before, after)
        rows.append((kind != "exposure", f"| `{method} {path}` | {role} | {before} | {after} | {text} |"))
    rows.sort(key=lambda r: r[0])
    return "\n".join(["| Request | Role | Before | After | What it means |", "|---|---|---|---|---|"] + [r[1] for r in rows])


def format_table(rows, roles):
    """Markdown table: one line per endpoint, one cell per role ('before -> after', marked if changed)."""
    by_endpoint = {}
    for (method, path, role), b, a in rows:
        by_endpoint.setdefault((method, path), {})[role] = (b, a)
    lines = ["| Endpoint | " + " | ".join(roles) + " |", "|---|" + "---|" * len(roles)]
    for (method, path), cells in by_endpoint.items():
        out = []
        for role in roles:
            b, a = cells.get(role, (None, None))
            out.append(f"{b}" if b == a else f"**{b} → {a}**")
        lines.append(f"| `{method} {path}` | " + " | ".join(out) + " |")
    return "\n".join(lines)


def _wait_ready(proc, port, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            return False
        with socket.socket() as s:
            s.settimeout(1)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(1)
    return False


def run_probe(mvn, app_dir, spec, port, startup_timeout=240):
    """Start the app with `spring-boot:run`, probe it, always stop it. Raises RuntimeError if it won't start."""
    mvn = str(Path(mvn).resolve()) if os.sep in mvn else mvn
    with tempfile.NamedTemporaryFile("w+", suffix=".log") as log:
        proc = subprocess.Popen(
            [mvn, "-q", "-B", "spring-boot:run", f"-Dspring-boot.run.arguments=--server.port={port}"],
            cwd=app_dir, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            if not _wait_ready(proc, port, startup_timeout):
                log.seek(0)
                raise RuntimeError("app did not start:\n" + "\n".join(log.read().splitlines()[-15:]))
            return probe(port, spec)
        finally:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                proc.wait(timeout=20)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass


def check(mvn, before_dir, after_dir, spec_path, ports=(18080, 18081)):
    """Run both builds and compare. Returns (rows, diffs, roles) or raises RuntimeError."""
    spec = load_spec(spec_path)
    before = run_probe(mvn, before_dir, spec, ports[0])
    after = run_probe(mvn, after_dir, spec, ports[1])
    rows, diffs = compare(before, after)
    return rows, diffs, list(spec["users"])
