#!/usr/bin/env python3
"""Side by side, from the terminal: OpenRewrite alone vs OpenRewrite + the agent, on one Spring Boot 2.7 app.

    python3 agent/compare.py                    # sample-app
    python3 agent/compare.py sample-jpa-app
    python3 agent/compare.py /path/to/your/app  # any Maven app whose tests pass on Spring Boot 2.x

Prints a table of what each approach achieved and then the code each one left behind. Both upgraded copies
are kept under the temp folder printed at the end so you can open them, and the originals are never touched.
"""
import argparse
import difflib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
# outside the repo on purpose: OpenRewrite skips folders that a .gitignore ignores
DEMO_ROOT = Path(tempfile.gettempdir()) / "boot-upgrade-demo"
RED, GREEN, BOLD, DIM, RESET = "\033[31m", "\033[32m", "\033[1m", "\033[2m", "\033[0m"


def column(summary, seconds):
    """The cells for one approach: [(row label, text)]."""
    score = summary.get("score")
    if score is None:
        compiles = "?"
    elif score >= 1000:
        compiles = f"NO ({score - 1000} compile errors)"
    else:
        compiles = "yes"
    tests = summary.get("tests")
    diffs, checks = summary.get("security_diffs"), summary.get("security_checks")
    return [
        ("Upgrade tool", "OpenRewrite" if str(summary.get("tool", "")).startswith("OpenRewrite") else "built-in fallback (OpenRewrite did NOT run)"),
        ("Result", "PASS" if summary.get("ok") else "FAILED"),
        ("Compiles", compiles),
        ("Tests passed", f"{tests[1]}/{tests[0]}" if tests else "none ran"),
        ("Model fix rounds", str(summary.get("model_rounds", "-"))),
        ("Security answers that changed", "-" if diffs is None else f"{diffs} of {checks}"),
        ("Time", f"{round(seconds)} s"),
    ]


def render_table(left_title, left, right_title, right):
    labels = [label for label, _ in left]
    widths = [max(len(label) for label in labels), max(len(left_title), *(len(t) for _, t in left)),
              max(len(right_title), *(len(t) for _, t in right))]
    line = "  ".join("-" * w for w in widths)
    out = ["  ".join(h.ljust(w) for h, w in zip(("", left_title, right_title), widths, strict=True)), line]
    for (label, a), (_, b) in zip(left, right, strict=True):
        out.append("  ".join(c.ljust(w) for c, w in zip((label, a, b), widths, strict=True)))
    return "\n".join(out)


def colorize(diff_lines, color):
    if not color:
        return diff_lines
    out = []
    for line in diff_lines:
        if line.startswith("+") and not line.startswith("+++"):
            out.append(GREEN + line + RESET)
        elif line.startswith("-") and not line.startswith("---"):
            out.append(RED + line + RESET)
        else:
            out.append(line)
    return out


def unified(original, new, name, limit=60):
    """Unified diff lines (without file headers), cut to `limit` lines."""
    lines = list(difflib.unified_diff(original.splitlines(), new.splitlines(), f"your {name}", f"upgraded {name}", lineterm="", n=2))
    lines = [ln for ln in lines if not ln.startswith(("---", "+++"))]
    if len(lines) > limit:
        lines = lines[:limit] + [f"... ({len(lines) - limit} more lines; see the upgraded copy)"]
    return lines or ["(no changes)"]


def interesting_files(src, a_dir, b_dir, only=None):
    """Java files whose upgraded text differs between the two approaches, as (name, original, a, b)."""
    found = []
    for f in sorted((src / "src" / "main").rglob("*.java")):
        rel = f.relative_to(src)
        a, b = (a_dir / rel), (b_dir / rel)
        if not (a.exists() and b.exists()):
            continue
        if only and f.name != only:
            continue
        if a.read_text() != b.read_text():
            found.append((f.name, f.read_text(), a.read_text(), b.read_text()))
    return found


def run_agent(app, work, report, extra, log_dir):
    cmd = [sys.executable, "-I", str(ROOT / "migrate.py"), str(app), "--work", str(work), "--report", str(report),
           "--log-dir", str(log_dir)] + extra
    spec = ROOT / "heldout" / f"{Path(app).name}.endpoints.json"
    if "heldout" in Path(app).parts and spec.exists():
        cmd += ["--endpoints", str(spec)]
    start = time.time()
    subprocess.run(cmd)
    summary_file = Path(report).with_suffix(".json")
    summary = json.loads(summary_file.read_text()) if summary_file.exists() else {}
    return summary, time.time() - start


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("app", nargs="?", default=str(REPO / "sample-app"), help="Spring Boot 2.x Maven app (its tests must pass)")
    ap.add_argument("--model", default="qwen2.5-coder:7b-instruct")
    ap.add_argument("--file", help="show only this Java file, for example SecurityConfig.java")
    ap.add_argument("--lines", type=int, default=60, help="max diff lines shown per file")
    ap.add_argument("--no-color", action="store_true")
    ap.add_argument("--skip-security-check", action="store_true", help="faster: do not start the apps to compare answers")
    args = ap.parse_args(argv)

    src = Path(args.app).resolve()
    out = DEMO_ROOT / src.name
    color = sys.stdout.isatty() and not args.no_color
    bold = (lambda s: f"{BOLD}{s}{RESET}") if color else (lambda s: s)
    dim = (lambda s: f"{DIM}{s}{RESET}") if color else (lambda s: s)
    sec = ["--skip-security-check"] if args.skip_security_check else []

    print(bold(f"\n=== 1/2  OpenRewrite alone (no model) on {src.name} ==="))
    alone, t_alone = run_agent(src, out / "openrewrite-alone", out / "openrewrite-alone.md",
                               ["--max-attempts", "0", "--skip-baseline-check", "--skip-security-check"], out / "logs")
    print(bold(f"\n=== 2/2  OpenRewrite + the agent ({args.model}) on {src.name} ==="))
    agent, t_agent = run_agent(src, out / "with-agent", out / "with-agent.md", ["--model", args.model] + sec, out / "logs")

    print(bold("\n=== Comparison ===\n"))
    print(render_table("OpenRewrite alone", column(alone, t_alone), "OpenRewrite + agent", column(agent, t_agent)))

    files = interesting_files(src, out / "openrewrite-alone", out / "with-agent", args.file)
    for name, original, a, b in files:
        print(bold(f"\n=== {name}: what each approach left behind (diff against your original) ==="))
        print(bold("\nOpenRewrite alone:"))
        print("\n".join(colorize(unified(original, a, name, args.lines), color)))
        print(bold("\nOpenRewrite + agent:"))
        print("\n".join(colorize(unified(original, b, name, args.lines), color)))
    if not files:
        print(dim("\n(The two approaches produced the same Java code.)"))

    print(bold("\n=== Where to look ==="))
    print(f"  upgraded copies : {out}/openrewrite-alone  and  {out}/with-agent")
    print(f"  full reports    : {out}/openrewrite-alone.md  and  {out}/with-agent.md")
    print(f"  what the model saw and answered, round by round: {out}/logs/")
    print(dim("  your original app was not modified."))


if __name__ == "__main__":
    main()
