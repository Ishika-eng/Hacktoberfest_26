"""Deterministic build-file migrations the model is not allowed to make.

The fix loop may only edit `src/main`. A few Spring Boot 2 -> 3 problems live in `pom.xml` instead, so they are
handled here by small, auditable rules that run once, right after the upgrade tool and before the integrity
hashes are taken. Every rule reports what it changed; the report prints it. Add a rule only for a change that
was verified on a real project.
"""
import re

# Verified on spring-petclinic-rest: 6.6.0 generates Jakarta code and compiles and passes. The 7.x versions tried
# (7.8.0, 7.12.0, 7.26.0) double-escaped quotes inside example JSON for that spec and did not compile.
OPENAPI_GENERATOR_VERSION = "6.6.0"


def _version_tuple(text):
    return tuple(int(p) for p in re.findall(r"\d+", text)[:3])


def openapi_generator_jakarta(pom_text):
    """Spring OpenAPI generator: use a version that can emit Jakarta code and switch that on.

    Boot 3 needs `jakarta.*`; generator 6.0.x emits `javax.*` and has no option to change it, which leaves
    hundreds of compile errors in code generated at build time. Returns (new_text, [what changed]).
    """
    if "openapi-generator-maven-plugin" not in pom_text or "<generatorName>spring</generatorName>" not in pom_text:
        return pom_text, []
    text, changes = pom_text, []
    prop = re.search(r"(<openapi-generator-maven-plugin\.version>)([^<]+)(</openapi-generator-maven-plugin\.version>)", text)
    if prop and _version_tuple(prop.group(2)) < _version_tuple(OPENAPI_GENERATOR_VERSION):
        text = text.replace(prop.group(0), f"{prop.group(1)}{OPENAPI_GENERATOR_VERSION}{prop.group(3)}")
        changes.append(f"openapi-generator-maven-plugin {prop.group(2)} -> {OPENAPI_GENERATOR_VERSION}")
    if "<useSpringBoot3>" not in text:
        new = re.sub(r"(<configOptions>)", r"\1\n                                <useSpringBoot3>true</useSpringBoot3>", text, count=1)
        if new != text:
            text = new
            changes.append("openapi-generator configOptions: useSpringBoot3 = true (generate jakarta.* code)")
    return text, changes


RULES = (openapi_generator_jakarta,)


def apply_build_rules(work):
    """Apply every rule to the work copy's pom.xml. Returns the list of changes made (empty if none)."""
    pom = work / "pom.xml"
    if not pom.exists():
        return []
    text, applied = pom.read_text(), []
    for rule in RULES:
        text, changes = rule(text)
        applied += changes
    if applied:
        pom.write_text(text)
    return applied
