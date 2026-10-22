#!/usr/bin/env python3
"""Spring Boot 2 -> 3 upgrade agent.

1. Copy the app to a work dir and apply the mechanical upgrade (stand-in for OpenRewrite).
2. Build + test. On failure, send each broken file and its error to an open-weight model.
3. Apply the fix, retest (max attempts). Write a report; flag anything unfixed for a human.
"""
import difflib, json, os, re, shutil, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT.parent / "sample-app").resolve()
WORK = ROOT.parent / "migrated-app"
MODEL = os.environ.get("MODEL", "qwen2.5-coder:7b-instruct")
OLLAMA = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OPENAI_BASE = os.environ.get("OPENAI_BASE_URL")  # set to use a hosted open-weight model instead
MVN = os.environ.get("MVN", "mvn")
MAX_ATTEMPTS = int(os.environ.get("MAX_ATTEMPTS", "3"))
BOOT3 = os.environ.get("BOOT3_VERSION", "3.3.5")
CHEATSHEET = (ROOT / "cheatsheet.md").read_text()


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def mechanical_upgrade(work):
    pom = work / "pom.xml"
    text = re.sub(r"(<artifactId>spring-boot-starter-parent</artifactId>\s*<version>)[^<]+",
                  rf"\g<1>{BOOT3}", pom.read_text())
    pom.write_text(text)
    for f in work.rglob("*.java"):
        s = f.read_text()
        n = re.sub(r"\bjavax\.(persistence|validation|servlet|annotation|transaction)\b", r"jakarta.\1", s)
        if n != s:
            f.write_text(n)


def ask_model(prompt):
    if OPENAI_BASE:
        url, body = f"{OPENAI_BASE}/chat/completions", {"model": MODEL, "temperature": 0,
              "messages": [{"role": "user", "content": prompt}]}
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {os.environ.get('API_KEY','')}"}
    else:
        url, body = f"{OLLAMA}/api/chat", {"model": MODEL, "stream": False, "options": {"temperature": 0},
              "messages": [{"role": "user", "content": prompt}]}
        headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, json.dumps(body).encode(), headers)
    with urllib.request.urlopen(req, timeout=600) as r:
        data = json.load(r)
    return data["choices"][0]["message"]["content"] if OPENAI_BASE else data["message"]["content"]


def extract_java(reply):
    m = re.search(r"```(?:java)?\s*\n(.*?)```", reply, re.S)
    return (m.group(1) if m else reply).strip() + "\n"


def broken_files(output, work):
    """Source files named in compiler errors or in failing-test stack traces."""
    found = {}
    for m in re.finditer(r"(/[^\n:\[]+?\.java)[:\[]", output):  # paths may contain spaces
        p = Path(m.group(1))
        if p.exists() and work in p.parents and "src/main" in str(p):
            found.setdefault(p, []).append(m.group(0))
    if found:
        return list(found)
    # Runtime failures (e.g. missing bean) carry no source path: match stack frames
    # `(Name.java:12)` and `Name.class` mentions back to app sources by file name.
    names = set(re.findall(r"\(([A-Za-z0-9_$]+)\.java:\d+\)", output))
    names |= set(re.findall(r"([A-Za-z0-9_]+)\.class\]", output))
    for p in sorted((work / "src" / "main").rglob("*.java")):
        if p.stem in names:
            found[p] = []
    return list(found)


def trim(output, limit=3500):
    lines = [l for l in output.splitlines() if "ERROR" in l or "FAIL" in l or "Caused by" in l]
    return "\n".join(lines)[:limit] or output[-limit:]


def fix_file(path, error):
    prompt = f"""You are migrating a Spring Boot 2.7 app to Spring Boot 3 (Spring Security 6, Java 17).
The build or tests failed. Fix the file below so it compiles and keeps the SAME behaviour.

Migration notes:
{CHEATSHEET}
Build error:
{error}

File {path.name}:
```java
{path.read_text()}
```
Reply with the complete corrected file in a single ```java block and nothing else."""
    return extract_java(ask_model(prompt))


def main():
    if WORK.exists():
        shutil.rmtree(WORK)
    shutil.copytree(SRC, WORK, ignore=shutil.ignore_patterns("target"))
    originals = {f: f.read_text() for f in WORK.rglob("*.java")}
    print(f"[1/3] mechanical upgrade -> Spring Boot {BOOT3}")
    mechanical_upgrade(WORK)

    log, ok, edited = [], False, []
    for attempt in range(1, MAX_ATTEMPTS + 2):
        print(f"[2/3] build + test (run {attempt})")
        code, out = run([MVN, "-q", "-B", "test"], WORK)
        if code == 0:
            ok = True
            break
        if attempt > MAX_ATTEMPTS:
            break
        files = broken_files(out, WORK)
        if not files:  # Maven trims stack traces: fall back to what the model already touched
            files = [f for f in edited if f.exists()]
        err = trim(out)
        log.append((attempt, [f.name for f in files], err))
        if not files:
            print("   no source file identified in the error; stopping")
            break
        for f in files:
            print(f"   model={MODEL} fixing {f.name}")
            f.write_text(fix_file(f, err))
            if f not in edited:
                edited.append(f)

    changes = []
    for f in sorted(WORK.rglob("*.java")):
        before, after = originals.get(f, ""), f.read_text()
        if before != after:
            changes.append("".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                                      f"a/{f.name}", f"b/{f.name}")))
    report = ["# Migration report", f"- Model: `{MODEL}`", f"- Target: Spring Boot {BOOT3}",
              f"- Result: **{'tests PASS' if ok else 'NEEDS HUMAN REVIEW (tests failing)'}**",
              f"- Model fix rounds: {len(log)}", "", "## Diff", "```diff", *changes, "```"]
    if not ok:
        report += ["", "## Last build error", "```", trim(out), "```"]
    (ROOT.parent / "REPORT.md").write_text("\n".join(report))
    print(f"[3/3] {'PASS' if ok else 'FAILED'} - report written to REPORT.md")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
