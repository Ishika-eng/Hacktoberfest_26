#!/usr/bin/env python3
"""Run the agent over a matrix of apps and models and write BENCHMARK.md.

    python3 agent/bench.py                       # defaults: both sample apps, three models + upgrade-tool-only baseline
    python3 agent/bench.py --models llama3.1:8b  # add or replace models (Ollama tags)

Per-run reports, machine-readable summaries and per-round prompts/replies go to reports/benchmark/.
"""
import argparse
import datetime
import json
import os
import platform
import re
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
OUT = REPO / "reports" / "benchmark"
WORK_ROOT = Path(tempfile.gettempdir()) / "boot-upgrade-bench"  # outside the repo: OpenRewrite skips git-ignored folders


def hardware():
    chip = platform.processor() or platform.machine()
    try:
        chip = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True).stdout.strip() or chip
        mem = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout) // 2**30
        return f"{chip}, {mem} GB RAM, {platform.system()} {platform.release()}"
    except (ValueError, OSError):
        return f"{chip}, {platform.system()} {platform.release()}"


def parse_ollama_show(text):
    """architecture, parameters, context length and quantization from `ollama show MODEL`."""
    info = {}
    for line in text.splitlines():
        m = re.match(r"\s*(architecture|parameters|context length|quantization)\s+(\S.*?)\s*$", line)
        if m and m.group(1) not in info:
            info[m.group(1)] = m.group(2)
    return info


def ollama_version():
    try:
        out = subprocess.run(["ollama", "--version"], capture_output=True, text=True).stdout
    except OSError:
        return "unknown"
    m = re.search(r"(\d+\.\d+\.\d+\S*)", out)
    return m.group(1) if m else "unknown"


def model_details(model):
    """One-line description of a local model: parameters, quantization, digest."""
    if not model or model.endswith("-cloud"):
        return "cloud-hosted" if model else ""
    try:
        info = parse_ollama_show(subprocess.run(["ollama", "show", model], capture_output=True, text=True).stdout)
        listing = subprocess.run(["ollama", "list"], capture_output=True, text=True).stdout
    except OSError:
        return "unknown"
    digest = next((ln.split()[1] for ln in listing.splitlines() if ln.split()[:1] == [model]), "?")
    return (f"{info.get('parameters', '?')} parameters, {info.get('quantization', '?')} quantization, "
            f"{info.get('architecture', '?')}, digest `{digest}`")


def code_version():
    """(agent commit, commit the cheat sheet last changed in, uncommitted changes in agent/?)."""
    def git(*args):
        try:
            return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout.strip()
        except OSError:
            return ""
    return (git("rev-parse", "--short", "HEAD") or "unknown", git("log", "-1", "--format=%h", "--", "agent/cheatsheet") or "unknown",
            bool(git("status", "--porcelain", "--", "agent")))


def slug(text):
    return re.sub(r"[^A-Za-z0-9.]+", "-", text).strip("-")


def run_one(app, model, repeat=1, repeats=1):
    """Run the agent once. model=None means upgrade tool only. Returns the summary dict plus wall time."""
    name = f"{slug(app)}__{slug(model) if model else 'upgrade-tool-only'}" + (f"__run{repeat}" if repeats > 1 else "")
    report = OUT / f"{name}.md"
    cmd = [sys.executable, "-I", str(ROOT / "migrate.py"), str(REPO / app), "--report", str(report),
           "--work", str(WORK_ROOT / f"migrated-{name}"), "--log-dir", str(OUT / "logs")]
    spec = ROOT / "heldout" / f"{Path(app).name}.endpoints.json"
    if app.startswith("heldout/") and spec.exists():
        cmd += ["--endpoints", str(spec)]
    cmd += ["--model", model] if model else ["--max-attempts", "0"]
    start = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, env=os.environ)
    elapsed = time.time() - start
    summary_file = report.with_suffix(".json")
    summary = json.loads(summary_file.read_text()) if summary_file.exists() else {"error": proc.stdout[-400:] + proc.stderr[-400:]}
    summary.update(app=app, model=model, repeat=repeat, seconds=round(elapsed), exit_code=proc.returncode, report=f"{name}.md")
    if model and not model.endswith("-cloud"):
        subprocess.run(["ollama", "stop", model], capture_output=True)  # free memory
    return summary


def cell_tests(s):
    t = s.get("tests")
    return f"{t[1]}/{t[0]}" if isinstance(t, list) and t else "-"


def result_text(s):
    if "error" in s and "ok" not in s:
        return "did not run"
    if s.get("model_error"):
        return "model unavailable"
    if s.get("test_files_modified"):
        return "INVALID (tests modified)"
    if s["ok"]:
        d = s.get("security_diffs")
        return "pass" + (f", {d} security difference(s) flagged" if d else "")
    return "fail (flagged for a human)"


def passed(s):
    return bool(s.get("ok")) and not s.get("test_files_modified")


def group(results):
    """[(app, model, [summaries])] in first-seen order."""
    groups, model_order, app_order = {}, {}, {}
    for s in results:
        groups.setdefault((s["app"], s["model"]), []).append(s)
        app_order.setdefault(s["app"], len(app_order))
        model_order.setdefault(s["model"], len(model_order))
    keys = sorted(groups, key=lambda k: (app_order[k[0]], -1 if k[1] is None else model_order[k[1]]))
    return [(a, m, groups[(a, m)]) for a, m in keys]


def determinism(runs):
    """Whether repeated runs produced byte-identical code, judged by the output fingerprint."""
    hashes = [r.get("output_hash") for r in runs]
    if len(runs) < 2 or not all(hashes):
        return "n/a (1 run)" if len(runs) < 2 else "unknown"
    distinct = len(set(hashes))
    return f"yes, all {len(runs)} runs" if distinct == 1 else f"no, {distinct} different outputs in {len(runs)} runs"


def table(results):
    lines = ["| App | Model | Runs passed | Tests passed per run | Model rounds per run | Median time | Security diffs per run | Same code every run? |",
             "|---|---|---|---|---|---|---|---|"]
    for app, model, runs in group(results):
        name = model or "none (upgrade tool only)"
        if (model or "").endswith("-cloud"):
            name += " (cloud-hosted)"
        sec = ", ".join("-" if r.get("security_diffs") is None else f"{r['security_diffs']}/{r['security_checks']}" for r in runs)
        lines.append(f"| `{app}` | {name} | {sum(passed(r) for r in runs)}/{len(runs)} | "
                     f"{', '.join(cell_tests(r) for r in runs)} | {', '.join(str(r.get('model_rounds', '-')) for r in runs)} | "
                     f"{round(statistics.median(r['seconds'] for r in runs))} s | {sec} | {determinism(runs)} |")
    return "\n".join(lines)


def write_markdown(results, path, extra=""):
    models = [m for m in dict.fromkeys(r["model"] for r in results) if m]
    details = "\n".join(f"- `{m}`: {model_details(m)}" for m in models)
    version = code_version()
    used_fallback = [r for r in results if r.get("tool", "").startswith("built-in") and r.get("fallback_reason")
                     and not r["fallback_reason"].startswith("OpenRewrite was disabled")]
    fallback_warning = (f"\n**Warning: {len(used_fallback)} run(s) used the built-in fallback because OpenRewrite failed** (for example the held-out app, which has Gradle files). Those rows are not OpenRewrite results; see each report." if used_fallback else "")
    dirty_note = " (**warning: uncommitted changes in agent/ when this ran**)" if version[2] else ""
    held = [a for a in dict.fromkeys(r["app"] for r in results) if a.startswith("heldout/")]
    held_note = ("\n**Held-out apps** (not written by us, pinned commits in `agent/heldout/manifest.json`): "
                 + ", ".join(f"`{a}`" for a in held) + ". The cheat sheet was frozen before these runs; see `agent/heldout/README.md`.\n"
                 if held else "")
    text = f"""# Benchmark

Each row is one model on one app, run several times with `agent/migrate.py`. Generated by `agent/bench.py` on {datetime.date.today()}.

**Hardware:** {hardware()}
**Agent version:** commit `{version[0]}`; the cheat sheet was last changed in `{version[1]}`{dirty_note}
**Ollama:** {ollama_version()}
**Models:**
{details}
**Upgrade tool:** OpenRewrite `UpgradeSpringBoot_3_3` (rewrite-spring 6.37.1), then the model fixes what is left.{fallback_warning}
**Sampling:** temperature 0, seed 0, 8192-token context, up to 5 model rounds, 30 s per-test timeout.
{held_note}
{table(results)}

How to read it:
- *Runs passed*: runs that ended with all tests green and passed every integrity check (same tests executed as the Boot 2 baseline, no test or build file changed). A pass can still carry security differences.
- *Tests passed* is passed/total in the final build. The first row of each app, with no model, is the baseline: what OpenRewrite alone achieves (an app that does not compile runs no tests, shown as `-`).
- *Security diffs* is endpoint checks whose HTTP status differs between the Boot 2 build and the upgraded build, out of all checks (every role x the endpoints in the app's `endpoints.json`). A pass with differences means the tests are green but behaviour changed.
- *Same code every run?* compares a fingerprint of the generated sources. With temperature 0 and a fixed seed on the same machine the output is often identical; where it is, the repeated runs are one result seen several times, not independent samples. Where it is not, small differences between rows are noise.
- Times include model loading. Per-round prompts and replies are in `reports/benchmark/logs/`; full reports are in `reports/benchmark/`.
{extra}
Reproduce: `python3 agent/bench.py` (needs Ollama with the models pulled, JDK 17+, Maven).
"""
    Path(path).write_text(text)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apps", nargs="+", default=["sample-app", "sample-jpa-app"])
    ap.add_argument("--models", nargs="*", default=["qwen2.5-coder:7b-instruct", "deepseek-coder:6.7b"])
    ap.add_argument("--no-baseline", action="store_true", help="skip the upgrade-tool-only row")
    ap.add_argument("--repeats", type=int, default=3, help="runs per cell (the upgrade-tool-only baseline is deterministic and runs once)")
    ap.add_argument("--repeats-for", nargs="*", default=[], metavar="MODEL=N",
                    help="override --repeats for a model, for example deepseek-coder:6.7b=2 (slow models need fewer runs)")
    ap.add_argument("--resume", action="store_true", help="keep finished runs in results.json and only run what is missing")
    ap.add_argument("--output", default=str(REPO / "BENCHMARK.md"))
    args = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    per_model = {k: int(v) for k, _, v in (item.rpartition("=") for item in args.repeats_for)}
    results_file = OUT / "results.json"
    results = json.loads(results_file.read_text()) if args.resume and results_file.exists() else []
    done = {(r["app"], r["model"], r["repeat"]) for r in results}
    for model in ([] if args.no_baseline else [None]) + list(args.models):  # models in the order given: slowest last
        repeats = 1 if model is None else per_model.get(model, args.repeats)
        for app in args.apps:
            for i in range(1, repeats + 1):
                if (app, model, i) in done:
                    print(f"== {app} / {model or 'upgrade tool only'} (run {i}/{repeats}) already done", flush=True)
                    continue
                print(f"== {app} / {model or 'upgrade tool only'} (run {i}/{repeats})", flush=True)
                results.append(run_one(app, model, i, repeats))
                print("  ->", result_text(results[-1]), cell_tests(results[-1]), f"{results[-1]['seconds']}s", flush=True)
                results_file.write_text(json.dumps(results, indent=2))
    write_markdown(results, args.output)
    print("wrote", args.output)


if __name__ == "__main__":
    main()
