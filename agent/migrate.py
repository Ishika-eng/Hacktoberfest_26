#!/usr/bin/env python3
"""Spring Boot 2 -> 3 upgrade agent.

1. Copy the app to a work dir (the original is never touched) and run the upgrade tool:
   OpenRewrite's Spring Boot 3 recipe, or a small built-in fallback.
2. Build + test. On failure, send the broken file and its error to an open-weight model.
3. Apply the fix and retest. A round that makes things worse is rolled back; tests can never be edited.
4. Compare endpoint access rules before and after, write a report, flag the rest for a human.
"""
import argparse
import datetime
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
sys.path.insert(0, str(ROOT))
import cves  # noqa: E402
import securitydiff  # noqa: E402

MODEL = os.environ.get("MODEL", "qwen2.5-coder:7b-instruct")
OLLAMA = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OPENAI_BASE = os.environ.get("OPENAI_BASE_URL")  # set to use a hosted open-weight model instead
MVN = os.environ.get("MVN", "mvn")
MVN = str(Path(MVN).resolve()) if os.sep in MVN else MVN
MAX_ATTEMPTS = int(os.environ.get("MAX_ATTEMPTS", "5"))
BOOT3 = os.environ.get("BOOT3_VERSION", "3.3.5")  # used by the built-in fallback only
OPENREWRITE_PLUGIN = os.environ.get("OPENREWRITE_PLUGIN", "6.46.1")
OPENREWRITE_SPRING = os.environ.get("OPENREWRITE_SPRING", "6.37.1")
OPENREWRITE_RECIPE = os.environ.get("OPENREWRITE_RECIPE", "org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_3")
TEST_TIMEOUT = "-Djunit.jupiter.execution.timeout.default=30s"


# ---------------------------------------------------------------- environment

def java_major(version_output):
    """Major Java version from `java -version` output, or None."""
    m = re.search(r'version "(\d+)(?:\.(\d+))?', version_output)
    if not m:
        return None
    major = int(m.group(1))
    return int(m.group(2)) if major == 1 and m.group(2) else major  # "1.8.0" -> 8


def check_java():
    try:
        p = subprocess.run(["java", "-version"], capture_output=True, text=True)
    except FileNotFoundError:
        sys.exit("error: java not found. Spring Boot 3 needs JDK 17 or newer.")
    major = java_major(p.stdout + p.stderr)
    if major is None or major < 17:
        sys.exit(f"error: JDK 17+ required for Spring Boot 3, found {major or 'unknown'}. "
                 "Install a newer JDK and rerun.")


def load_cheatsheet(directory=None):
    """All migration notes, one file per topic (contributors add a file in agent/cheatsheet/)."""
    d = Path(directory) if directory else ROOT / "cheatsheet"
    return "\n".join(f.read_text().strip() + "\n" for f in sorted(d.glob("*.md")))


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


# ---------------------------------------------------------------- upgrade tools

def boot_version(work):
    m = re.search(r"<artifactId>spring-boot-starter-parent</artifactId>\s*<version>([^<]+)", (work / "pom.xml").read_text())
    return m.group(1) if m else None


def mechanical_upgrade(work):
    """Fallback upgrade: parent version bump and javax -> jakarta."""
    pom = work / "pom.xml"
    pom.write_text(re.sub(r"(<artifactId>spring-boot-starter-parent</artifactId>\s*<version>)[^<]+",
                          rf"\g<1>{BOOT3}", pom.read_text()))
    for f in work.rglob("*.java"):
        s = f.read_text()
        n = re.sub(r"\bjavax\.(persistence|validation|servlet|annotation|transaction)\b", r"jakarta.\1", s)
        if n != s:
            f.write_text(n)


def openrewrite_upgrade(work):
    """Run OpenRewrite's Spring Boot 3 recipe. True if it ran and the parent is now 3.x."""
    code, out = run([MVN, "-B", "-q", f"org.openrewrite.maven:rewrite-maven-plugin:{OPENREWRITE_PLUGIN}:run",
                     f"-Drewrite.recipeArtifactCoordinates=org.openrewrite.recipe:rewrite-spring:{OPENREWRITE_SPRING}",
                     f"-Drewrite.activeRecipes={OPENREWRITE_RECIPE}"], work)
    version = boot_version(work) or ""
    return code == 0 and version.startswith("3."), out


# ---------------------------------------------------------------- test integrity

def hash_tests(work):
    """{relative path: sha256} for everything under src/test."""
    root = work / "src" / "test"
    return {str(f.relative_to(work)): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in sorted(root.rglob("*")) if f.is_file()} if root.exists() else {}


def changed_tests(baseline, current):
    """Paths of test files that were added, removed or modified relative to the baseline."""
    return sorted(p for p in set(baseline) | set(current) if baseline.get(p) != current.get(p))


def write_source(work, path, text):
    """Only application sources under src/main may be written by the fix loop."""
    path = Path(path).resolve()
    if (work / "src" / "main").resolve() not in path.parents:
        raise PermissionError(f"refusing to write outside src/main: {path}")
    path.write_text(text)


# ---------------------------------------------------------------- build scoring

def parse_score(code, out):
    """Lower is better. 0 = green. Compile errors always score worse than failing tests."""
    if code == 0:
        return 0
    compile_errors = set(re.findall(r"([^\s/]+\.java:\[\d+,\d+\])", out))
    if "COMPILATION ERROR" in out or compile_errors:
        return 1000 + len(compile_errors)
    totals = re.findall(r"Tests run: (\d+), Failures: (\d+), Errors: (\d+)", out)
    if totals:
        _, failures, errors = totals[-1]
        return max(1, int(failures) + int(errors))
    return 500


def tests_summary(out):
    totals = re.findall(r"Tests run: (\d+), Failures: (\d+), Errors: (\d+)", out)
    if not totals:
        return None
    run_, failures, errors = map(int, totals[-1])
    return run_, run_ - failures - errors


def count_tests(work):
    """(total, passed) from Maven's surefire XML reports in the work dir, or None. Skipped tests are not passed."""
    total = bad = 0
    for f in (work / "target" / "surefire-reports").glob("TEST-*.xml"):
        head = f.read_text()[:2000]
        attrs = {k: re.search(rf'<testsuite [^>]*\b{k}="(\d+)"', head) for k in ("tests", "failures", "errors", "skipped")}
        if attrs["tests"]:
            total += int(attrs["tests"].group(1))
            bad += sum(int(m.group(1)) for k, m in attrs.items() if k != "tests" and m)
    return (total, total - bad) if total else None


def build(work):
    """One `mvn test`. Old surefire reports are removed first so the counts always describe this build."""
    shutil.rmtree(work / "target" / "surefire-reports", ignore_errors=True)
    return run([MVN, "-q", "-B", TEST_TIMEOUT, "test"], work)


def hash_build_files(work):
    """Hashes of every pom.xml and everything under .mvn: the files that decide which tests run."""
    files = [f for f in work.rglob("pom.xml") if "target" not in f.parts]
    files += [f for f in (work / ".mvn").rglob("*") if f.is_file()] if (work / ".mvn").exists() else []
    return {str(f.relative_to(work)): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(files)}


SKIP_MARKERS = {
    "skipTests": r"<skipTests>\s*true", "maven.test.skip": r"maven\.test\.skip", "-DskipTests": r"-DskipTests",
    "testFailureIgnore": r"<testFailureIgnore>\s*true", "surefire <skip>": r"<skip>\s*true\s*</skip>",
    "surefire excludes": r"<excludes?>\s*<exclude>[^<]*[Tt]est",
}


def test_skipping_markers(pom_text):
    """Settings in a pom that make Maven skip, ignore failures in, or exclude tests."""
    return sorted(name for name, pattern in SKIP_MARKERS.items() if re.search(pattern, pom_text))


def output_hash(work):
    """One hash over all application sources, to tell whether repeated runs produced identical code."""
    h = hashlib.sha256()
    for f in sorted((work / "src" / "main").rglob("*")):
        if f.is_file():
            h.update(str(f.relative_to(work)).encode() + f.read_bytes())
    return h.hexdigest()[:12]


def snapshot(work):
    return {f: f.read_text() for f in sorted((work / "src" / "main").rglob("*.java"))}


def restore(work, snap):
    for f, text in snap.items():
        write_source(work, f, text)


# ---------------------------------------------------------------- model

def ask_model(prompt):
    if OPENAI_BASE:
        url, body = f"{OPENAI_BASE}/chat/completions", {"model": MODEL, "temperature": 0, "seed": 0,
              "messages": [{"role": "user", "content": prompt}]}
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {os.environ.get('API_KEY', '')}"}
    else:
        url, body = f"{OLLAMA}/api/chat", {"model": MODEL, "stream": False,
              "options": {"temperature": 0, "seed": 0, "num_ctx": 8192},
              "messages": [{"role": "user", "content": prompt}]}
        headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, json.dumps(body).encode(), headers)
    with urllib.request.urlopen(req, timeout=600) as r:
        data = json.load(r)
    return data["choices"][0]["message"]["content"] if OPENAI_BASE else data["message"]["content"]


def extract_java(reply):
    m = re.search(r"```(?:java)?\s*\n(.*?)```", reply, re.S)
    return (m.group(1) if m else reply).strip() + "\n"


# ---------------------------------------------------------------- error analysis

def broken_files(output, work):
    """Source files named in compiler errors, failing-test stack traces or the error text."""
    found = {}
    for m in re.finditer(r"(/[^\n:\[]+?\.java)[:\[]", output):  # paths may contain spaces
        p = Path(m.group(1))
        if p.exists() and work in p.parents and "src/main" in str(p):
            found.setdefault(p, []).append(m.group(0))
    if found:
        return list(found)
    # Runtime failures carry no source path: match stack frames `(Name.java:12)` and `Name.class`.
    names = set(re.findall(r"\(([A-Za-z0-9_$]+)\.java:\d+\)", output))
    names |= set(re.findall(r"([A-Za-z0-9_]+)\.class\]", output))
    sources = sorted((work / "src" / "main").rglob("*.java"))
    for p in sources:
        if p.stem in names:
            found[p] = []
    if found:
        return list(found)
    # Last resort: application classes whose name appears in the error text (at most 3).
    words = set(re.findall(r"\b[A-Z][A-Za-z0-9_]+\b", output))
    return [p for p in sources if p.stem in words][:3]


def choose_files(score, out, work, edited, originals):
    """Which files to hand to the model.

    Compile errors name their file. Test failures do not: the stack trace points at framework glue and at
    application classes that merely ran. So for test failures prefer the files the model already edited (a
    behaviour regression most likely comes from its own rewrite), then files the upgrade tool changed, and
    use the stack-trace guess only when nothing else is known.
    """
    named = broken_files(out, work)
    still_there = [f for f in edited if f.exists()]
    if score >= 1000:  # compile errors
        return named or still_there
    if still_there:
        return still_there
    changed = [f for f in sorted((work / "src" / "main").rglob("*.java")) if f.read_text() != originals.get(f, "")]
    return [f for f in changed if f in named] or changed[:3] or named


def trim(output, limit=3500):
    lines = [ln for ln in output.splitlines() if "ERROR" in ln or "FAIL" in ln or "Caused by" in ln]
    return "\n".join(lines)[:limit] or output[-limit:]


def errors_for(path, out, limit=3500):
    """Only the compiler errors that mention this file, plus lines that name no file at all."""
    blocks, cur = [], []
    for line in trim(out, 10**6).splitlines():
        if re.search(r"\.java:\[\d+,\d+\]", line):  # a new compile error
            if cur:
                blocks.append(cur)
            cur = [line]
        elif cur and re.match(r"\[ERROR\]\s+(symbol|location|required|found|reason):", line):
            cur.append(line)  # detail lines belong to the error above
        else:
            if cur:
                blocks.append(cur)
                cur = []
            blocks.append([line])
    if cur:
        blocks.append(cur)
    keep = [b for b in blocks if path.name in "\n".join(b) or ".java:[" not in "\n".join(b)]
    return "\n".join(line for b in keep for line in b)[:limit] or trim(out, limit)


def reply_matches_file(path, text):
    """A reply for Foo.java must declare Foo; otherwise the model answered about the wrong file."""
    return re.search(rf"\b(class|interface|enum|record|@interface)\s+{re.escape(path.stem)}\b", text) is not None


def diagnose(prompt):
    """A short model-written explanation for the human. Never raises; None if the model is unavailable."""
    try:
        return ask_model(prompt).strip()[:1500]
    except (OSError, KeyError, ValueError):
        return None


def failing_tests(output, work, limit=3):
    """Source of the failing tests: shows the model what behaviour the app must keep."""
    seen, snippets = set(), []
    for cls, meth in re.findall(r"\[ERROR\]\s+(\w+Tests?)\.(\w+)[:\s]", output):
        if (cls, meth) in seen:
            continue
        seen.add((cls, meth))
        for f in (work / "src" / "test").rglob(f"{cls}.java"):
            m = re.search(rf"[^\n]*\bvoid {meth}\(.*?\n    \}}\n", f.read_text(), re.S)
            if m:
                snippets.append(m.group(0).strip())
        if len(snippets) >= limit:
            break
    return "\n\n".join(snippets)


KNOWN_IMPORTS = {  # Spring Security 6 classes small models often import from the wrong package
    "Customizer": "org.springframework.security.config.Customizer",
    "SecurityFilterChain": "org.springframework.security.web.SecurityFilterChain",
    "AuthenticationConfiguration":
        "org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration",
    "AuthenticationManager": "org.springframework.security.authentication.AuthenticationManager",
    "UserDetailsService": "org.springframework.security.core.userdetails.UserDetailsService",
    "User": "org.springframework.security.core.userdetails.User",
    "InMemoryUserDetailsManager": "org.springframework.security.provisioning.InMemoryUserDetailsManager",
    "PasswordEncoder": "org.springframework.security.crypto.password.PasswordEncoder",
    "BCryptPasswordEncoder": "org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder",
    "AbstractHttpConfigurer": "org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer",
    "HttpMethod": "org.springframework.http.HttpMethod",
}


def repair_imports(path, output):
    """Like an IDE's auto-import: fix `cannot find symbol: class X` for known classes. True if edited."""
    text = path.read_text()
    new = text
    for name in set(re.findall(r"symbol:\s+class (\w+)", output)):
        body = re.sub(r"^import [^\n]+\n", "", new, flags=re.M)
        if not re.search(rf"\b{name}\b", body):  # unused import of a class that no longer exists
            new = re.sub(rf"^import (?:static )?[\w.]+\.{name};\n", "", new, flags=re.M)
            continue
        fq = KNOWN_IMPORTS.get(name)
        if not fq:
            continue
        new = re.sub(rf"^import (?!{re.escape(fq)};)[\w.]+\.{name};\n", "", new, flags=re.M)  # wrong package
        if f"import {fq};" not in new:
            new = re.sub(r"(^package [^\n]+\n)", rf"\1\nimport {fq};\n", new, count=1, flags=re.M)
    if new != text:
        path.write_text(new)
        return True
    return False


def build_prompt(path, error, original, current, cheatsheet, tests="", rejected=""):
    tests_block = f"\nFailing tests (the behaviour the app must have):\n```java\n{tests}\n```\n" if tests else ""
    rejected_block = (f"\nA previous attempt at this file was REJECTED because it made the build worse. "
                      f"Do not repeat it:\n```java\n{rejected}\n```\n") if rejected else ""
    return f"""You are migrating a Spring Boot 2.7 app to Spring Boot 3 (Spring Security 6, Hibernate 6, Java 17).
The build or tests failed. Fix the file below so it compiles and keeps the SAME behaviour as the original.
Every feature the original enables (for example HTTP Basic auth, CSRF settings, URL rules, users, beans) must still be enabled.
Comments like /*~~(Migrate manually ...)~~>*/ were left by OpenRewrite where it could not migrate; handle them and delete the marker.

Migration notes:
{cheatsheet}
Build error:
{error}
{tests_block}{rejected_block}
ORIGINAL Spring Boot 2.7 version of {path.name} (this is the behaviour to preserve):
```java
{original}
```

CURRENT version of {path.name} (this is what fails):
```java
{current}
```
Reply with the complete corrected file in a single ```java block and nothing else."""


# ---------------------------------------------------------------- run

def parse_args(argv=None):
    ap = argparse.ArgumentParser(description="Upgrade a Spring Boot 2.7 app to Spring Boot 3 with a local open-weight model.")
    ap.add_argument("app", nargs="?", default=str(REPO / "sample-app"), help="path to the Spring Boot 2.x app")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--max-attempts", type=int, default=MAX_ATTEMPTS, help="model fix rounds; 0 = upgrade tool only")
    ap.add_argument("--no-openrewrite", action="store_true", help="use the built-in fallback upgrade")
    ap.add_argument("--skip-security-check", action="store_true")
    ap.add_argument("--skip-baseline-check", action="store_true",
                    help="do not first run the original app's tests (needed to verify the executed-test count)")
    ap.add_argument("--endpoints", help="endpoints.json for the security check (default: <app>/endpoints.json)")
    ap.add_argument("--cve-scan", action="store_true", help="count known advisories via osv.dev (sends dependency coordinates)")
    ap.add_argument("--work", help="where the upgraded copy goes (default: ./migrated-<app>)")
    ap.add_argument("--report", help="report path (default: ./REPORT.md)")
    ap.add_argument("--log-dir", default=str(REPO / "runs"), help="per-round prompts and replies are saved here")
    return ap.parse_args(argv)


def slug(text):
    return re.sub(r"[^A-Za-z0-9.]+", "-", text).strip("-")


def fresh_copy(src, work):
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(src, work, ignore=shutil.ignore_patterns("target", ".git"))


def main(argv=None):
    global MODEL, MAX_ATTEMPTS
    args = parse_args(argv)
    MODEL, MAX_ATTEMPTS = args.model, args.max_attempts
    check_java()

    src = Path(args.app).resolve()
    work = Path(args.work).resolve() if args.work else REPO / f"migrated-{src.name}"
    report_path = Path(args.report).resolve() if args.report else REPO / "REPORT.md"
    log_dir = Path(args.log_dir) / f"{src.name}-{slug(MODEL)}-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    cheatsheet = load_cheatsheet()

    fresh_copy(src, work)
    baseline_count = None
    if not args.skip_baseline_check:
        print("[0/4] baseline: the original app must pass its own tests")
        code, out = build(work)
        baseline_count = count_tests(work)
        if code != 0 or not baseline_count:
            sys.exit("error: the original app does not pass its own tests (or runs none), so an upgrade cannot be "
                     "checked against it.\n" + trim(out, 1500))
        shutil.rmtree(work / "target", ignore_errors=True)
    original_markers = test_skipping_markers((src / "pom.xml").read_text()) if (src / "pom.xml").exists() else []
    originals = {f: f.read_text() for f in work.rglob("*.java")}
    tests_before_upgrade = hash_tests(work)

    tool = "built-in fallback"
    if not args.no_openrewrite:
        print(f"[1/4] OpenRewrite {OPENREWRITE_RECIPE}")
        ok_tool, tool_out = openrewrite_upgrade(work)
        if ok_tool:
            tool = f"OpenRewrite (rewrite-spring {OPENREWRITE_SPRING})"
        else:
            print("   OpenRewrite failed; using the built-in fallback\n   " + trim(tool_out, 500).replace("\n", "\n   "))
            fresh_copy(src, work)
    if tool == "built-in fallback":
        print(f"[1/4] built-in upgrade -> Spring Boot {BOOT3}")
        mechanical_upgrade(work)
    target = boot_version(work)
    tests_baseline = hash_tests(work)
    build_baseline = hash_build_files(work)
    touched_by_tool = changed_tests(tests_before_upgrade, tests_baseline)

    rounds, rejected, edited = [], {}, []
    best = None  # (score, snapshot, output)
    model_rounds = iterations = 0
    model_error = None
    ok = False
    while True:
        iterations += 1
        print(f"[2/4] build + test (run {iterations})")
        code, out = build(work)
        score = parse_score(code, out)
        action = "build"
        if best is None or score < best[0]:
            best = (score, snapshot(work), out)
        elif score > best[0]:
            for f, text in snapshot(work).items():
                if text != best[1].get(f):
                    rejected[f] = text
            restore(work, best[1])
            action = f"rolled back (score {score} is worse than {best[0]})"
            print(f"   {action}")
            score, out = best[0], best[2]
        rounds.append({"run": iterations, "score": score, "summary": tests_summary(out), "action": action})
        if code == 0:
            ok = True
            break
        if model_rounds >= MAX_ATTEMPTS or iterations > MAX_ATTEMPTS * 3 + 3:
            break

        files = choose_files(score, out, work, edited, originals)
        if not files:
            print("   no source file identified in the error; stopping")
            break
        repaired = [f for f in files if repair_imports(f, out)]
        if repaired:  # deterministic auto-import fix; rebuild before spending a model call
            print(f"   auto-import repaired {', '.join(f.name for f in repaired)}")
            rounds[-1]["action"] += f"; auto-import fix in {', '.join(f.name for f in repaired)}"
            continue
        model_rounds += 1
        tests, notes = failing_tests(out, work), []
        for f in files:
            print(f"   model={MODEL} fixing {f.name}")
            prompt = build_prompt(f, errors_for(f, out), originals.get(f, ""), f.read_text(), cheatsheet, tests,
                                  rejected.get(f, ""))
            try:
                reply = ask_model(prompt)
            except (OSError, KeyError, ValueError) as e:  # URLError/HTTPError are OSErrors
                model_error = f"{type(e).__name__}: {e}"
                print(f"   model unavailable: {model_error}")
                break
            new_text = extract_java(reply)
            log_dir.mkdir(parents=True, exist_ok=True)
            (log_dir / f"round-{model_rounds}-{f.stem}.md").write_text(
                (f"# Round {model_rounds}: {f.name}\n\nModel: `{MODEL}`\n\n## Prompt\n\n{prompt}\n\n## Reply\n\n{reply}\n")
                .replace(str(REPO), "<project>"))
            if not reply_matches_file(f, new_text):
                print(f"   reply rejected: it does not declare {f.stem}")
                notes.append(f"reply for {f.name} rejected (wrong class)")
                continue
            write_source(work, f, new_text)
            notes.append(f"model fixed {f.name}")
            if f not in edited:
                edited.append(f)
        if model_error:
            rounds[-1]["action"] += f"; model unavailable ({model_error})"
            break
        rounds[-1]["action"] += "; " + ", ".join(notes)

    if not ok and best is not None:  # leave the best state we saw, not the last one
        restore(work, best[1])
        out = best[2]
    violations = changed_tests(tests_baseline, hash_tests(work))
    violations += [f"{p} (build file changed after the upgrade tool)" for p in changed_tests(build_baseline, hash_build_files(work))]
    pom_now = work / "pom.xml"
    new_markers = sorted(set(test_skipping_markers(pom_now.read_text()) if pom_now.exists() else []) - set(original_markers))
    if new_markers:
        violations.append("pom.xml now contains test-skipping settings: " + ", ".join(new_markers))
    final_count = count_tests(work) if ok else None
    if ok and baseline_count and final_count != baseline_count:
        violations.append(f"executed tests {final_count} differ from the Boot 2 baseline {baseline_count} (total, passed)")
    ok = ok and not violations

    sec_rows = sec_diffs = sec_roles = sec_error = None
    spec = Path(args.endpoints) if args.endpoints else src / "endpoints.json"
    if not args.skip_security_check and spec.exists() and best[0] < 1000:
        print("[3/4] security equivalence check (Boot 2 vs upgraded)")
        try:
            sec_rows, sec_diffs, sec_roles = securitydiff.check(MVN, src, work, spec)
        except RuntimeError as e:
            sec_error = str(e)

    cve = None
    if args.cve_scan:
        print("[3/4] advisory scan (osv.dev)")
        try:
            cve = (cves.scan(MVN, src), cves.scan(MVN, work))
        except Exception as e:  # network or Maven problems should not fail the run
            cve = str(e)

    diagnosis = None
    if MAX_ATTEMPTS > 0 and not model_error and (not ok or sec_diffs):
        if not ok:
            diagnosis = diagnose(
                "A Spring Boot 2.7 app was upgraded to Spring Boot 3 automatically but the build or tests still fail.\n"
                f"Last build error:\n{trim(best[2])}\n\nIn at most 5 sentences, tell a developer what is most likely wrong "
                "and what to check first. Do not invent code.")
        else:
            changed = "\n".join(f"{m} {p} as {r}: {b} -> {a} ({securitydiff.describe(b, a)[1]})"
                                for (m, p, r), b, a in sec_diffs)
            diagnosis = diagnose(
                "After upgrading a Spring Boot 2.7 app to Spring Boot 3 all tests pass, but these requests now get "
                f"different HTTP status codes:\n{changed}\n\nMigration notes:\n{cheatsheet}\n"
                "In at most 5 sentences, explain the most likely cause and whether a developer needs to act. Do not invent code.")

    write_report(report_path, locals())
    summary = {"app": src.name, "model": None if MAX_ATTEMPTS == 0 else MODEL, "tool": tool, "boot": target,
               "ok": ok, "score": best[0], "tests": (final_count if ok else tests_summary(best[2])),
               "baseline_tests": baseline_count, "output_hash": output_hash(work),
               "newly_accessible": None if sec_diffs is None else sum(securitydiff.describe(b, a)[0] == "exposure" for _, b, a in sec_diffs),
               "model_rounds": model_rounds, "runs": iterations, "model_error": model_error,
               "security_checks": None if sec_rows is None else len(sec_rows),
               "security_diffs": None if sec_diffs is None else len(sec_diffs),
               "test_files_modified": violations}
    report_path.with_suffix(".json").write_text(json.dumps(summary, indent=2))
    status = ("PASS" if ok else "FAILED") + (" (security behaviour differs)" if ok and sec_diffs else "")
    print(f"[4/4] {status} - report written to {report_path}")
    sys.exit(2 if violations else 0 if ok and not sec_diffs else 3 if ok else 1)


def write_report(path, v):
    ok, rounds, work, src = v["ok"], v["rounds"], v["work"], v["src"]
    verdict = ("tests PASS" if ok else "NEEDS HUMAN REVIEW (tests failing)")
    if v["violations"]:
        verdict = "INVALID: the test setup was changed or the tests that ran differ from the baseline"
    r = ["# Migration report", "",
         f"- App: `{src.name}`  |  Model: {'none (upgrade tool only)' if MAX_ATTEMPTS == 0 else '`' + MODEL + '`'}  |  Upgrade tool: {v['tool']}",
         f"- Spring Boot parent after upgrade: `{v['target']}`",
         f"- Result: **{verdict}**",
         f"- Model fix rounds: {v['model_rounds']} (max {MAX_ATTEMPTS})",
         f"- Settings: temperature 0, seed 0, 8192-token context; output fingerprint `{output_hash(work)}` "
         "(identical fingerprints across runs mean identical generated code)", ""]
    r += ["## Build score per run", "", "Score = failing tests, or 1000+ compile errors. 0 means green. "
          "A run that scores worse than the best so far is rolled back.", "",
          "| Run | Score | Tests passed | What happened |", "|---|---|---|---|"]
    for x in rounds:
        passed = f"{x['summary'][1]}/{x['summary'][0]}" if x["summary"] else ("all" if x["score"] == 0 else "-")
        r.append(f"| {x['run']} | {x['score']} | {passed} | {x['action']} |")
    base = v["baseline_count"]
    r += ["", "## Test integrity", "",
          "- Existing files under `src/test` (tests and test resources) and every `pom.xml` / `.mvn` file are hashed after the "
          "upgrade tool runs and again at the end. The fix loop can only write under `src/main`.",
          "- The upgraded pom must not gain test-skipping settings (`skipTests`, `maven.test.skip`, `testFailureIgnore`, "
          "surefire `skip` or excludes).",
          (f"- A passing run must execute exactly the baseline's tests: the original app ran {base[0]} tests, {base[1]} passed."
           if base else "- Baseline check skipped, so the executed-test count was not verified."),
          ("- **Violation: " + "; ".join(v["violations"]) + "**") if v["violations"] else "- Result: no violations."]
    if v["touched_by_tool"]:
        r += ["", "The upgrade tool itself (not the model) rewrote these test files: "
              + ", ".join(f"`{p}`" for p in v["touched_by_tool"])]
    if v["sec_rows"] is not None:
        d = v["sec_diffs"]
        exposed = sum(securitydiff.describe(b, a)[0] == "exposure" for _, b, a in d)
        r += ["", "## Security equivalence (same requests, Boot 2 build vs upgraded build)", "",
              f"{len(v['sec_rows'])} checks, **{len(d)} difference(s)**, of which **{exposed} newly accessible**. "
              "Cells show the HTTP status; changed cells show before → after. "
              "401/403 means denied; 404 means the route was not found, which is a different problem.",
              "", securitydiff.format_table(v["sec_rows"], v["sec_roles"])]
        if d:
            r += ["", "### What changed", "", securitydiff.format_differences(d), "",
                  "**Flagged for a human: the upgraded app answers some requests differently. "
                  "Review each before deploying" + (", starting with the newly accessible ones.**" if exposed else ".**")]
    elif v["sec_error"]:
        r += ["", "## Security equivalence", "", "Could not run:", "```", v["sec_error"], "```"]
    cve = v["cve"]
    if isinstance(cve, tuple):
        before, after = cve
        r += ["", "## Known advisories (osv.dev; not confirmed CVEs)", "",
              f"- Before: {len(before['advisories'])} advisories across {before['dependencies']} dependencies",
              f"- After: {len(after['advisories'])} advisories across {after['dependencies']} dependencies",
              "- These are advisories published for the exact dependency versions, not proof that your app is exploitable.",
              "- The agent does **not** bump dependencies itself. The drop comes only from the versions Spring Boot 3 manages, "
              "so the advisories below are still unpatched and need a human decision.", "",
              "<details><summary>Advisories that remain after the upgrade</summary>", ""]
        r += [f"- `{dep}`: {', '.join(ids)}" for dep, ids in sorted(after["affected"].items())] or ["- none"]
        r += ["", "</details>"]
    elif isinstance(cve, str):
        r += ["", "## Known advisories", "", f"Scan unavailable: {cve}"]
    changes = []
    for f in sorted(work.rglob("*.java")):
        before, after = v["originals"].get(f, ""), f.read_text()
        if before != after:
            changes.append("".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                                      f"a/{f.name}", f"b/{f.name}")))
    r += ["", "## Diff (all changes to Java sources, including the upgrade tool's)", "```diff", *changes, "```"]
    if v["diagnosis"]:
        r += ["", "## Diagnosis (written by the model; unverified, check before relying on it)", "", v["diagnosis"]]
    if v["model_error"]:
        r += ["", "## Model error", "", f"`{v['model_error']}`"]
    if not ok:
        r += ["", "## Last build error (best state)", "```", trim(v["out"]), "```"]
    Path(path).write_text("\n".join(r).replace(str(REPO), "<project>"))


if __name__ == "__main__":
    main()
