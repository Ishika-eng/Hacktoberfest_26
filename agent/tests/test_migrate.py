"""Unit tests for the agent. No Ollama, Maven or network needed: the model and the build are faked."""
import contextlib
import http.server
import importlib.util
import io
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    import sys
    sys.path.insert(0, str(ROOT))
    spec.loader.exec_module(mod)
    return mod


migrate = load("migrate")
securitydiff = load("securitydiff")
bench = load("bench")
compare = load("compare")
cves = load("cves")


class JavaVersion(unittest.TestCase):
    def test_modern_and_legacy_formats(self):
        self.assertEqual(migrate.java_major('openjdk version "21.0.12" 2026-07-21'), 21)
        self.assertEqual(migrate.java_major('java version "1.8.0_292"'), 8)
        self.assertEqual(migrate.java_major('openjdk version "17" 2021-09-14'), 17)
        self.assertIsNone(migrate.java_major("nonsense"))


class Scoring(unittest.TestCase):
    def test_green_is_zero(self):
        self.assertEqual(migrate.parse_score(0, ""), 0)

    def test_compile_errors_outrank_test_failures(self):
        compile_err = "[ERROR] COMPILATION ERROR :\n[ERROR] /x/A.java:[3,4] cannot find symbol\n[ERROR] /x/B.java:[1,2] x"
        test_fail = "[ERROR] Tests run: 11, Failures: 3, Errors: 1, Skipped: 0"
        self.assertEqual(migrate.parse_score(1, compile_err), 1002)
        self.assertEqual(migrate.parse_score(1, test_fail), 4)
        self.assertGreater(migrate.parse_score(1, compile_err), migrate.parse_score(1, test_fail))

    def test_failed_build_never_scores_zero(self):
        self.assertEqual(migrate.parse_score(1, "[ERROR] Tests run: 5, Failures: 0, Errors: 0"), 1)
        self.assertEqual(migrate.parse_score(1, "something odd"), 500)

    def test_uses_the_last_total_line(self):
        out = "Tests run: 5, Failures: 0, Errors: 2, Skipped: 0 - in A\nTests run: 11, Failures: 0, Errors: 2, Skipped: 0"
        self.assertEqual(migrate.parse_score(1, out), 2)
        self.assertEqual(migrate.tests_summary(out), (11, 9))


class BuildFileGuards(unittest.TestCase):
    def test_detects_settings_that_skip_tests(self):
        self.assertEqual(migrate.test_skipping_markers("<project><skipTests>true</skipTests></project>"), ["skipTests"])
        self.assertEqual(migrate.test_skipping_markers("<testFailureIgnore>true</testFailureIgnore>"), ["testFailureIgnore"])
        self.assertIn("maven.test.skip", migrate.test_skipping_markers("<maven.test.skip>true</maven.test.skip>"))
        self.assertEqual(migrate.test_skipping_markers("<project><skipTests>false</skipTests></project>"), [])

    def test_hashes_every_pom_and_mvn_file_but_not_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = Path(tmp)
            (w / "pom.xml").write_text("a")
            (w / "mod").mkdir()
            (w / "mod" / "pom.xml").write_text("b")
            (w / ".mvn").mkdir()
            (w / ".mvn" / "maven.config").write_text("-DskipTests")
            (w / "target").mkdir()
            (w / "target" / "pom.xml").write_text("ignored")
            self.assertEqual(sorted(migrate.hash_build_files(w)), [".mvn/maven.config", "mod/pom.xml", "pom.xml"])

    def test_test_resources_are_covered_by_the_test_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = Path(tmp)
            (w / "src" / "test" / "resources").mkdir(parents=True)
            (w / "src" / "test" / "resources" / "application.properties").write_text("x=1")
            self.assertIn("src/test/resources/application.properties", migrate.hash_tests(w))

    def test_output_hash_changes_with_the_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = Path(tmp)
            (w / "src" / "main").mkdir(parents=True)
            (w / "src" / "main" / "A.java").write_text("class A {}")
            first = migrate.output_hash(w)
            self.assertEqual(first, migrate.output_hash(w))
            (w / "src" / "main" / "A.java").write_text("class A { }")
            self.assertNotEqual(first, migrate.output_hash(w))


class CountingTests(unittest.TestCase):
    def test_reads_surefire_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "target" / "surefire-reports"
            d.mkdir(parents=True)
            (d / "TEST-A.xml").write_text('<testsuite name="A" tests="6" errors="0" skipped="0" failures="0">')
            (d / "TEST-B.xml").write_text('<testsuite name="B" tests="5" errors="1" skipped="0" failures="1">')
            (d / "TEST-C.xml").write_text('<testsuite name="C" tests="2" errors="0" skipped="2" failures="0">')
            self.assertEqual(migrate.count_tests(Path(tmp)), (13, 9))  # the 2 skipped tests do not count as passed
            self.assertIsNone(migrate.count_tests(Path(tmp) / "nowhere"))


class ModelReply(unittest.TestCase):
    def test_extracts_the_java_block(self):
        self.assertEqual(migrate.extract_java("Sure!\n```java\nclass A {}\n```\nDone"), "class A {}\n")

    def test_plain_reply_is_kept(self):
        self.assertEqual(migrate.extract_java("class A {}"), "class A {}\n")


class ImportRepair(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.file = Path(self.tmp.name) / "S.java"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, text):
        self.file.write_text(text)

    def test_wrong_package_is_replaced(self):
        self.write("package a;\n\nimport org.springframework.security.config.annotation.web.configurers.Customizer;\n\nclass S { Customizer c; }\n")
        self.assertTrue(migrate.repair_imports(self.file, "[ERROR]   symbol:   class Customizer\n"))
        text = self.file.read_text()
        self.assertIn("import org.springframework.security.config.Customizer;", text)
        self.assertNotIn("web.configurers.Customizer", text)

    def test_missing_import_is_added_once(self):
        self.write("package a;\n\nclass S { SecurityFilterChain c; }\n")
        out = "[ERROR]   symbol:   class SecurityFilterChain\n"
        self.assertTrue(migrate.repair_imports(self.file, out))
        self.assertFalse(migrate.repair_imports(self.file, out))
        self.assertEqual(self.file.read_text().count("import org.springframework.security.web.SecurityFilterChain;"), 1)

    def test_unused_import_of_a_removed_class_is_deleted(self):
        self.write("package a;\n\nimport x.y.WebSecurityConfigurerAdapter;\n\nclass S {}\n")
        self.assertTrue(migrate.repair_imports(self.file, "[ERROR]   symbol:   class WebSecurityConfigurerAdapter\n"))
        self.assertNotIn("WebSecurityConfigurerAdapter", self.file.read_text())

    def test_used_unknown_class_is_left_for_the_model(self):
        self.write("package a;\n\nimport x.y.Mystery;\n\nclass S { Mystery m; }\n")
        self.assertFalse(migrate.repair_imports(self.file, "[ERROR]   symbol:   class Mystery\n"))


class SettingsDoNotLeakBetweenRuns(unittest.TestCase):
    def test_a_zero_attempt_run_does_not_change_the_next_runs_default(self):
        migrate.MAX_ATTEMPTS = 0
        migrate.MODEL = "some-other-model"
        self.addCleanup(lambda: (setattr(migrate, "MAX_ATTEMPTS", migrate.DEFAULT_MAX_ATTEMPTS),
                                 setattr(migrate, "MODEL", migrate.DEFAULT_MODEL)))
        args = migrate.parse_args(["x"])
        self.assertEqual(args.max_attempts, migrate.DEFAULT_MAX_ATTEMPTS)
        self.assertEqual(args.model, migrate.DEFAULT_MODEL)


class MixedMavenGradle(unittest.TestCase):
    def test_gradle_files_are_removed_from_a_maven_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = Path(tmp)
            (w / "pom.xml").write_text("<project/>")
            (w / "build.gradle").write_text("x")
            (w / "gradlew").write_text("x")
            (w / "gradle" / "wrapper").mkdir(parents=True)
            (w / "src" / "main").mkdir(parents=True)
            (w / "src" / "main" / "A.java").write_text("class A {}")
            dropped = migrate.drop_gradle_files(w)
            self.assertEqual(sorted(dropped), ["build.gradle", "gradle/", "gradlew"])
            self.assertTrue((w / "pom.xml").exists())
            self.assertTrue((w / "src" / "main" / "A.java").exists())

    def test_a_gradle_only_project_is_left_alone(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = Path(tmp)
            (w / "build.gradle").write_text("x")
            self.assertEqual(migrate.drop_gradle_files(w), [])
            self.assertTrue((w / "build.gradle").exists())


class OverrideRepair(unittest.TestCase):
    def test_removes_an_override_the_compiler_rejects(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "S.java"
            f.write_text("class S {\n    @Bean\n    @Override\n    public int a() { return 1; }\n\n    @Override\n    public String toString() { return \"s\"; }\n}\n")
            out = "[ERROR] /x/S.java:[3,5] method does not override or implement a method from a supertype\n" * 2
            self.assertTrue(migrate.repair_overrides(f, out))
            text = f.read_text()
            self.assertEqual(text.count("@Override"), 1)  # only the rejected one went; toString() keeps its own
            self.assertIn("@Bean", text)
            self.assertFalse(migrate.repair_overrides(f, "all good"))

    def test_common_jpa_classes_are_known(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "Product.java"
            f.write_text("package a;\n\nclass Product { @Column(length = 10) String d; }\n")
            self.assertTrue(migrate.repair_known(f, "[ERROR]   symbol:   class Column\n"))
            self.assertIn("import jakarta.persistence.Column;", f.read_text())


class FindingBrokenFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.work = Path(self.tmp.name) / "my project" / "app"  # a space in the path on purpose
        self.main = self.work / "src" / "main" / "java"
        self.main.mkdir(parents=True)
        for n in ("A", "B", "Product"):
            (self.main / f"{n}.java").write_text("class %s {}" % n)

    def tearDown(self):
        self.tmp.cleanup()

    def test_compiler_path_with_spaces(self):
        out = f"[ERROR] {self.main / 'A.java'}:[3,4] cannot find symbol"
        self.assertEqual(migrate.broken_files(out, self.work), [self.main / "A.java"])

    def test_stack_frame_without_a_path(self):
        out = "at com.example.B.run(B.java:12)\nat org.junit.Foo.bar(Foo.java:1)"
        self.assertEqual(migrate.broken_files(out, self.work), [self.main / "B.java"])

    def test_class_name_in_error_text(self):
        out = "Caused by: could not store Product: value too long"
        self.assertEqual(migrate.broken_files(out, self.work), [self.main / "Product.java"])

    def test_nothing_found(self):
        self.assertEqual(migrate.broken_files("all good", self.work), [])


class ChoosingFiles(unittest.TestCase):
    """Test failures must not be blamed on the application classes that only show up in stack traces."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.work = Path(self.tmp.name)
        main = self.work / "src" / "main" / "java"
        main.mkdir(parents=True)
        self.files = {n: main / f"{n}.java" for n in ("SecurityConfig", "Order", "ShopApplication")}
        for n, f in self.files.items():
            f.write_text(f"class {n} {{}}")
        self.originals = {f: f.read_text() for f in self.files.values()}
        # a stack trace that mentions the application class and not the culprit
        self.trace = "at com.example.ShopApplication.main(ShopApplication.java:9)\nStatus expected:<401> but was:<403>"

    def tearDown(self):
        self.tmp.cleanup()

    def test_compile_errors_use_the_named_file(self):
        out = f"[ERROR] {self.files['Order']}:[3,4] cannot find symbol"
        chosen = migrate.choose_files(1001, out, self.work, [self.files["SecurityConfig"]], self.originals)
        self.assertEqual(chosen, [self.files["Order"]])

    def test_test_failures_go_back_to_files_the_model_edited(self):
        chosen = migrate.choose_files(3, self.trace, self.work, [self.files["SecurityConfig"]], self.originals)
        self.assertEqual(chosen, [self.files["SecurityConfig"]])  # not ShopApplication from the trace

    def test_without_edits_prefer_files_the_upgrade_tool_changed(self):
        self.files["Order"].write_text("class Order { /* upgraded */ }")
        chosen = migrate.choose_files(3, self.trace, self.work, [], self.originals)
        self.assertEqual(chosen, [self.files["Order"]])

    def test_the_stack_trace_guess_is_the_last_resort(self):
        chosen = migrate.choose_files(3, self.trace, self.work, [], self.originals)
        self.assertEqual(chosen, [self.files["ShopApplication"]])


class FailingTests(unittest.TestCase):
    def test_returns_the_test_method_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            d = work / "src" / "test" / "java"
            d.mkdir(parents=True)
            (d / "LoginTests.java").write_text(
                "class LoginTests {\n    @Test void logsIn() throws Exception {\n        go();\n    }\n\n"
                "    @Test void other() {\n    }\n}\n")
            snippet = migrate.failing_tests("[ERROR]   LoginTests.logsIn:22 Status expected:<200>", work)
            self.assertIn("void logsIn()", snippet)
            self.assertNotIn("other", snippet)


class TestIntegrity(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.work = Path(self.tmp.name)
        (self.work / "src" / "test").mkdir(parents=True)
        (self.work / "src" / "main").mkdir(parents=True)
        (self.work / "src" / "test" / "T.java").write_text("class T {}")

    def tearDown(self):
        self.tmp.cleanup()

    def test_detects_edit_add_and_delete(self):
        base = migrate.hash_tests(self.work)
        self.assertEqual(migrate.changed_tests(base, migrate.hash_tests(self.work)), [])
        (self.work / "src" / "test" / "T.java").write_text("class T { }")
        (self.work / "src" / "test" / "N.java").write_text("class N {}")
        self.assertEqual(migrate.changed_tests(base, migrate.hash_tests(self.work)),
                         ["src/test/N.java", "src/test/T.java"])

    def test_the_fix_loop_cannot_write_tests(self):
        with self.assertRaises(PermissionError):
            migrate.write_source(self.work, self.work / "src" / "test" / "T.java", "class T { hacked }")
        with self.assertRaises(PermissionError):
            migrate.write_source(self.work, self.work / "pom.xml", "x")
        migrate.write_source(self.work, self.work / "src" / "main" / "Ok.java", "class Ok {}")


class PerFileErrors(unittest.TestCase):
    OUT = ("[ERROR] COMPILATION ERROR :\n"
           "[ERROR] /p/src/A.java:[3,4] cannot find symbol\n"
           "[ERROR]   symbol:   class Foo\n"
           "[ERROR]   location: class A\n"
           "[ERROR] /p/src/B.java:[9,1] duplicate class\n"
           "[ERROR] Failed to execute goal compiler")

    def test_keeps_only_this_files_errors_and_generic_lines(self):
        a = migrate.errors_for(Path("A.java"), self.OUT)
        self.assertIn("class Foo", a)
        self.assertNotIn("duplicate class", a)
        self.assertIn("Failed to execute goal", a)
        b = migrate.errors_for(Path("B.java"), self.OUT)
        self.assertIn("duplicate class", b)
        self.assertNotIn("class Foo", b)

    def test_reply_must_declare_the_file_class(self):
        self.assertTrue(migrate.reply_matches_file(Path("S.java"), "public class S { }"))
        self.assertTrue(migrate.reply_matches_file(Path("R.java"), "public interface R { }"))
        self.assertFalse(migrate.reply_matches_file(Path("S.java"), "public class SecurityConfig { }"))


class Prompt(unittest.TestCase):
    def test_contains_original_current_error_and_rejected_attempt(self):
        p = migrate.build_prompt(Path("S.java"), "ERR", "ORIGINAL_SRC", "CURRENT_SRC", "NOTES", "TEST_SRC", "BAD_TRY")
        for needle in ("ERR", "ORIGINAL_SRC", "CURRENT_SRC", "NOTES", "TEST_SRC", "BAD_TRY", "REJECTED"):
            self.assertIn(needle, p)

    def test_optional_blocks_are_omitted(self):
        p = migrate.build_prompt(Path("S.java"), "ERR", "o", "c", "n")
        self.assertNotIn("REJECTED", p)
        self.assertNotIn("Failing tests", p)


class CheatSheet(unittest.TestCase):
    def test_loads_every_file_in_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "20-b.md").write_text("BBB")
            (Path(tmp) / "10-a.md").write_text("AAA")
            text = migrate.load_cheatsheet(tmp)
            self.assertLess(text.index("AAA"), text.index("BBB"))

    def test_repository_cheatsheet_is_not_empty(self):
        self.assertIn("SecurityFilterChain", migrate.load_cheatsheet())


class FakeApp:
    """A tiny project plus scripted build output, to run the real main() loop without Maven or a model."""

    def __init__(self, tmp, outputs):
        self.src = Path(tmp) / "app"
        (self.src / "src" / "main" / "java").mkdir(parents=True)
        (self.src / "src" / "test" / "java").mkdir(parents=True)
        (self.src / "pom.xml").write_text(
            "<project><parent><artifactId>spring-boot-starter-parent</artifactId><version>2.7.18</version></parent></project>")
        (self.src / "src" / "main" / "java" / "S.java").write_text("class S { /* original */ }")
        (self.src / "src" / "test" / "java" / "T.java").write_text("class T {}")
        self.outputs = list(outputs)
        self.prompts = []
        self.builds = 0
        self.tamper = False
        self.pom_tamper = False
        self.test_counts = []  # tests executed by each green build (default 1)

    def fake_run(self, cmd, cwd):
        self.builds += 1
        if self.tamper:
            (Path(cwd) / "src" / "test" / "java" / "T.java").write_text("class T { /* edited */ }")
        if self.pom_tamper and self.builds > 1:
            pom = Path(cwd) / "pom.xml"
            pom.write_text(pom.read_text() + "<skipTests>true</skipTests>")
        out = self.outputs.pop(0).replace("{FILE}", str(Path(cwd) / "src" / "main" / "java" / "S.java"))
        if out == "OK":
            n = self.test_counts.pop(0) if self.test_counts else 1
            reports = Path(cwd) / "target" / "surefire-reports"
            reports.mkdir(parents=True, exist_ok=True)
            (reports / "TEST-T.xml").write_text(f'<testsuite name="T" tests="{n}" errors="0" skipped="0" failures="0">')
        return (0 if out == "OK" else 1), out


class AgentLoop(unittest.TestCase):
    COMPILE_1 = "[ERROR] COMPILATION ERROR :\n[ERROR] {FILE}:[1,1] cannot find symbol\n"
    COMPILE_3 = COMPILE_1 + "[ERROR] {FILE}:[2,1] x\n[ERROR] {FILE}:[3,1] y\n"

    def run_main(self, outputs, reply="class S { /* fixed */ }", max_attempts="5", tamper=False,
                 baseline=False, test_counts=None, pom_tamper=False):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        app = FakeApp(tmp.name, outputs)
        app.tamper = tamper
        app.pom_tamper = pom_tamper
        app.test_counts = list(test_counts or [])
        saved = (migrate.run, migrate.ask_model, migrate.check_java)
        migrate.run = app.fake_run
        migrate.ask_model = lambda prompt: (app.prompts.append(prompt), f"```java\n{reply}\n```")[1]
        migrate.check_java = lambda: None
        self.addCleanup(lambda: (setattr(migrate, "run", saved[0]), setattr(migrate, "ask_model", saved[1]),
                                 setattr(migrate, "check_java", saved[2])))
        work, report = Path(tmp.name) / "work", Path(tmp.name) / "REPORT.md"
        with self.assertRaises(SystemExit) as ctx, contextlib.redirect_stdout(io.StringIO()):
            migrate.main([str(app.src), "--no-openrewrite", "--skip-security-check", "--work", str(work),
                          "--report", str(report), "--log-dir", str(Path(tmp.name) / "runs"),
                          "--max-attempts", max_attempts] + ([] if baseline else ["--skip-baseline-check"]))
        return app, work, report, ctx.exception.code

    def test_fixes_and_passes(self):
        app, work, report, code = self.run_main([self.COMPILE_1, "OK"])
        self.assertEqual(code, 0)
        self.assertIn("fixed", (work / "src/main/java/S.java").read_text())
        self.assertIn("tests PASS", report.read_text())
        self.assertEqual(len(app.prompts), 1)

    def test_a_rewrite_that_only_misses_an_import_is_repaired_not_rolled_back(self):
        slip = ("[ERROR] COMPILATION ERROR :\n[ERROR] {FILE}:[1,10] cannot find symbol\n[ERROR]   symbol:   class Column\n"
                "[ERROR] {FILE}:[2,1] another\n")  # score 1002, worse than the starting 1001: would be rolled back
        app, work, report, code = self.run_main([self.COMPILE_1, slip, "OK"], reply="class S { @Column int d; }")
        self.assertEqual(code, 0)
        self.assertIn("import jakarta.persistence.Column;", (work / "src/main/java/S.java").read_text())
        text = report.read_text()
        self.assertIn("auto-repaired imports/@Override in S.java", text)
        self.assertNotIn("rolled back (score", text)  # no actual rollback entry (the intro sentence always says "rolled back")

    def test_the_upgrade_tool_only_row_gets_no_repairs(self):
        slip = "[ERROR] COMPILATION ERROR :\n[ERROR] {FILE}:[1,10] cannot find symbol\n[ERROR]   symbol:   class Column\n"
        app, work, report, code = self.run_main([slip], max_attempts="0")
        self.assertEqual(code, 1)
        self.assertNotIn("auto-repaired", report.read_text())

    def test_a_worse_round_is_rolled_back_and_remembered(self):
        app, work, report, code = self.run_main([self.COMPILE_1, self.COMPILE_3, self.COMPILE_3, "OK"],
                                                reply="class S { /* attempt */ }")
        self.assertEqual(code, 0)
        self.assertIn("rolled back", report.read_text())
        self.assertIn("REJECTED", app.prompts[1])  # the second prompt carries the rejected attempt

    def test_gives_up_with_best_state_and_exit_1(self):
        app, work, report, code = self.run_main([self.COMPILE_1] * 20, max_attempts="2")
        self.assertEqual(code, 1)
        self.assertEqual(len([p for p in app.prompts if "Reply with the complete corrected file" in p]), 2)
        self.assertEqual(len(app.prompts), 3)  # 2 fix rounds + 1 diagnosis
        text = report.read_text()
        self.assertIn("NEEDS HUMAN REVIEW", text)
        self.assertIn("Diagnosis (written by the model", text)

    def test_reply_for_the_wrong_class_is_never_written(self):
        app, work, report, code = self.run_main([self.COMPILE_1] * 20, reply="class Other { }", max_attempts="2")
        self.assertIn("original", (work / "src/main/java/S.java").read_text())
        self.assertIn("rejected (wrong class)", report.read_text())

    def test_zero_attempts_means_upgrade_tool_only(self):
        app, work, report, code = self.run_main([self.COMPILE_1], max_attempts="0")
        self.assertEqual(code, 1)
        self.assertEqual(app.prompts, [])
        self.assertIn("none (upgrade tool only)", report.read_text())

    def test_unavailable_model_ends_the_run_cleanly(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        app = FakeApp(tmp.name, [self.COMPILE_1] * 5)
        saved = (migrate.run, migrate.ask_model, migrate.check_java)
        self.addCleanup(lambda: (setattr(migrate, "run", saved[0]), setattr(migrate, "ask_model", saved[1]),
                                 setattr(migrate, "check_java", saved[2])))
        migrate.run, migrate.check_java = app.fake_run, lambda: None

        def down(prompt):
            raise ConnectionRefusedError("ollama is not running")
        migrate.ask_model = down
        report = Path(tmp.name) / "REPORT.md"
        with self.assertRaises(SystemExit) as ctx, contextlib.redirect_stdout(io.StringIO()):
            migrate.main([str(app.src), "--no-openrewrite", "--skip-security-check", "--skip-baseline-check",
                          "--work", str(Path(tmp.name) / "w"), "--report", str(report),
                          "--log-dir", str(Path(tmp.name) / "runs")])
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("ollama is not running", report.read_text())
        self.assertIn('"model_error"', report.with_suffix(".json").read_text())

    def test_modified_tests_invalidate_the_run(self):
        app, work, report, code = self.run_main(["OK"], tamper=True)
        self.assertEqual(code, 2)
        self.assertIn("INVALID", report.read_text())

    def test_baseline_count_must_match_the_final_run(self):
        app, work, report, code = self.run_main(["OK", self.COMPILE_1, "OK"], baseline=True, test_counts=[3, 3])
        self.assertEqual(code, 0)
        self.assertIn("original app ran 3 tests", report.read_text())

    def test_running_fewer_tests_than_the_baseline_invalidates_the_run(self):
        app, work, report, code = self.run_main(["OK", self.COMPILE_1, "OK"], baseline=True, test_counts=[3, 1])
        self.assertEqual(code, 2)
        text = report.read_text()
        self.assertIn("INVALID", text)
        self.assertIn("differ from the Boot 2 baseline", text)

    def test_a_red_original_app_stops_before_anything_else(self):
        app, work, report, code = self.run_main([self.COMPILE_1], baseline=True)
        self.assertIn("does not pass its own tests", str(code))  # sys.exit(message)
        self.assertEqual(app.prompts, [])  # nothing was attempted

    def test_editing_the_pom_to_skip_tests_invalidates_the_run(self):
        app, work, report, code = self.run_main(["OK", self.COMPILE_1, "OK"], baseline=True, test_counts=[1, 1],
                                                pom_tamper=True)
        self.assertEqual(code, 2)
        text = report.read_text()
        self.assertIn("build file changed", text)
        self.assertIn("test-skipping settings: skipTests", text)

    def test_original_app_is_never_modified(self):
        app, work, report, code = self.run_main([self.COMPILE_1, "OK"])
        self.assertIn("original", (app.src / "src/main/java/S.java").read_text())
        self.assertIn("2.7.18", (app.src / "pom.xml").read_text())


class SecurityDiff(unittest.TestCase):
    SPEC = {"users": {"anonymous": None, "admin": ["a", "pw"]},
            "endpoints": [{"method": "GET", "path": "/secret"}, {"method": "POST", "path": "/x", "json": {"k": 1}}]}

    def test_compare_flags_only_changes(self):
        before = {("GET", "/a", "anonymous"): 401, ("GET", "/b", "anonymous"): 200}
        after = {("GET", "/a", "anonymous"): 403, ("GET", "/b", "anonymous"): 200}
        rows, diffs = securitydiff.compare(before, after)
        self.assertEqual(len(rows), 2)
        self.assertEqual(diffs, [(("GET", "/a", "anonymous"), 401, 403)])

    def test_not_found_is_not_denied(self):
        self.assertEqual(securitydiff.category(404), "not found")
        self.assertEqual(securitydiff.category(401), "denied")
        self.assertEqual(securitydiff.category(403), "denied")
        self.assertEqual(securitydiff.category(405), "rejected")
        self.assertEqual(securitydiff.describe(200, 404)[0], "behaviour")
        self.assertIn("route no longer matches", securitydiff.describe(200, 404)[1])
        self.assertIn("access removed", securitydiff.describe(200, 403)[1])

    def test_something_becoming_accessible_is_an_exposure(self):
        for before in (401, 403, 404):
            self.assertEqual(securitydiff.describe(before, 200)[0], "exposure")
        self.assertIn("NEWLY ACCESSIBLE", securitydiff.describe(401, 200)[1])

    def test_exposures_are_listed_first(self):
        diffs = [(("GET", "/a", "u"), 200, 404), (("GET", "/b", "u"), 401, 200)]
        lines = securitydiff.format_differences(diffs).splitlines()
        self.assertIn("/b", lines[2])
        self.assertIn("/a", lines[3])

    def test_table_marks_changed_cells(self):
        rows, _ = securitydiff.compare({("GET", "/a", "anonymous"): 401}, {("GET", "/a", "anonymous"): 404})
        self.assertIn("**401 → 404**", securitydiff.format_table(rows, ["anonymous"]))

    def test_probe_sends_roles_and_bodies(self):
        seen = []

        class Handler(http.server.BaseHTTPRequestHandler):
            def _answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length).decode() if length else ""
                seen.append((self.command, self.path, self.headers.get("Authorization"), body))
                self.send_response(200 if self.headers.get("Authorization") else 401)
                self.end_headers()
            do_GET = do_POST = _answer

            def log_message(self, *args):
                pass

        server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        results = securitydiff.probe(server.server_port, self.SPEC)
        self.assertEqual(results[("GET", "/secret", "anonymous")], 401)
        self.assertEqual(results[("GET", "/secret", "admin")], 200)
        self.assertEqual(results[("POST", "/x", "admin")], 200)
        self.assertTrue(any(body == '{"k": 1}' for _, _, _, body in seen))


class BenchmarkTable(unittest.TestCase):
    def test_groups_repeats_into_one_row(self):
        runs = [
            {"app": "a", "model": "m", "ok": True, "tests": [11, 11], "model_rounds": 1, "seconds": 60,
             "security_diffs": 0, "security_checks": 18},
            {"app": "a", "model": "m", "ok": False, "tests": [11, 9], "model_rounds": 5, "seconds": 200},
            {"app": "a", "model": None, "ok": False, "tests": None, "model_rounds": 0, "seconds": 13},
        ]
        text = bench.table(runs)
        self.assertIn("| `a` | m | 1/2 | 11/11, 9/11 | 1, 5 | 130 s | 0/18, - | unknown |", text)
        self.assertIn("none (upgrade tool only) | 0/1 | -", text)


class GitIgnoredFolders(unittest.TestCase):
    """OpenRewrite silently skips git-ignored folders; the agent must notice and say so."""

    def test_detects_a_folder_inside_a_repo_that_ignores_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess = __import__("subprocess")
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            (repo / ".gitignore").write_text("out/\n")
            (repo / "out").mkdir()
            (repo / "kept").mkdir()
            self.assertTrue(migrate.git_ignored(repo / "out"))
            self.assertFalse(migrate.git_ignored(repo / "kept"))

    def test_a_folder_outside_any_repo_is_not_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(migrate.git_ignored(Path(tmp)))

    def test_exit_zero_without_a_version_bump_is_reported_as_no_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / "pom.xml").write_text("<parent><artifactId>spring-boot-starter-parent</artifactId><version>2.7.18</version></parent>")
            saved = migrate.run
            migrate.run = lambda cmd, cwd: (0, "")
            self.addCleanup(lambda: setattr(migrate, "run", saved))
            ok, _, why = migrate.openrewrite_upgrade(work)
            self.assertFalse(ok)
            self.assertIn("changed nothing", why)

    def test_default_work_folder_is_outside_the_repository(self):
        self.assertNotIn(str(migrate.REPO), str(migrate.OUT_ROOT))


class ComparisonTable(unittest.TestCase):
    def test_says_when_openrewrite_did_not_run(self):
        cells = dict(compare.column({"tool": "built-in fallback", "ok": False, "score": 1006}, 12))
        self.assertIn("did NOT run", cells["Upgrade tool"])
        self.assertEqual(cells["Compiles"], "NO (6 compile errors)")
        self.assertEqual(cells["Tests passed"], "none ran")

    def test_a_passing_run(self):
        cells = dict(compare.column({"tool": "OpenRewrite (rewrite-spring 6.37.1)", "ok": True, "score": 0, "tests": [11, 11],
                                     "model_rounds": 2, "security_diffs": 0, "security_checks": 18}, 62))
        self.assertEqual(cells["Upgrade tool"], "OpenRewrite")
        self.assertEqual(cells["Tests passed"], "11/11")
        self.assertEqual(cells["Security answers that changed"], "0 of 18")

    def test_diff_is_cut_to_the_limit(self):
        lines = compare.unified("\n".join(str(i) for i in range(100)), "\n".join(str(i + 1) for i in range(100)), "A.java", limit=5)
        self.assertEqual(len(lines), 6)
        self.assertIn("more lines", lines[-1])


class BenchmarkDetails(unittest.TestCase):
    SHOW = """  Model
    architecture        qwen2
    parameters          7.6B
    context length      32768
    embedding length    3584
    quantization        Q4_K_M

  Capabilities
    completion
"""

    def test_parses_ollama_show(self):
        self.assertEqual(bench.parse_ollama_show(self.SHOW),
                         {"architecture": "qwen2", "parameters": "7.6B", "context length": "32768", "quantization": "Q4_K_M"})

    def test_same_fingerprint_means_the_runs_are_one_result(self):
        same = [{"output_hash": "abc"}, {"output_hash": "abc"}, {"output_hash": "abc"}]
        self.assertEqual(bench.determinism(same), "yes, all 3 runs")
        mixed = [{"output_hash": "a"}, {"output_hash": "b"}, {"output_hash": "a"}]
        self.assertEqual(bench.determinism(mixed), "no, 2 different outputs in 3 runs")
        self.assertEqual(bench.determinism([{"output_hash": "a"}]), "n/a (1 run)")
        self.assertEqual(bench.determinism([{}, {}]), "unknown")


class CodeVersion(unittest.TestCase):
    def test_reports_commit_cheatsheet_commit_and_dirty_flag(self):
        head, sheet, dirty = bench.code_version()
        self.assertTrue(head)
        self.assertTrue(sheet)
        self.assertIsInstance(dirty, bool)


class BenchmarkOrder(unittest.TestCase):
    def test_rows_are_sorted_by_app_then_baseline_then_model_order(self):
        def r(app, model, ok=True):
            return {"app": app, "model": model, "ok": ok, "tests": [1, 1], "seconds": 1, "model_rounds": 0}
        # results arrive models-first (slowest model last), but the table groups them per app
        results = [r("a", None), r("b", None), r("a", "fast"), r("b", "fast"), r("a", "slow"), r("b", "slow")]
        rows = [(app, model) for app, model, _ in bench.group(results)]
        self.assertEqual(rows, [("a", None), ("a", "fast"), ("a", "slow"), ("b", None), ("b", "fast"), ("b", "slow")])


class Advisories(unittest.TestCase):
    def test_parses_maven_dependency_list(self):
        text = ("\nThe following files have been resolved:\n"
                "   org.springframework:spring-core:jar:5.3.31:compile\n"
                "   io.netty:netty-x:jar:linux-x86_64:4.1.0:runtime\n")
        self.assertEqual(cves.parse_dependency_list(text),
                         [("io.netty:netty-x", "4.1.0"), ("org.springframework:spring-core", "5.3.31")])

    def test_query_osv_groups_ids_by_dependency(self):
        def fake_post(body):
            self.assertEqual(body["queries"][0]["package"]["ecosystem"], "Maven")
            return {"results": [{"vulns": [{"id": "GHSA-1"}, {"id": "CVE-2"}]}, {}]}
        found = cves.query_osv([("a:b", "1.0"), ("c:d", "2.0")], post=fake_post)
        self.assertEqual(found, {"a:b:1.0": ["CVE-2", "GHSA-1"]})


if __name__ == "__main__":
    unittest.main()
