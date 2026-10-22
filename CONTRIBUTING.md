# Contributing

Thanks for helping. The most useful contributions are small and testable.

## Setup

You need Python 3.10+, JDK 17+, Maven and (to run models) [Ollama](https://docs.ollama.com/quickstart). The agent has no Python dependencies.

```bash
pip install -r requirements-dev.txt          # only for lint
python3 -I -m unittest discover -s agent/tests -t agent
ruff check agent
```

The unit tests fake the model and the build, so they run without Ollama or Maven.

## Ways to contribute

- **Add a cheat sheet entry.** One file per topic in `agent/cheatsheet/` (`NN-topic.md`), written as short rules the model can follow: what the old API was, what the Boot 3 form is. Prefer a failing test in a sample app that proves the entry is needed.
- **Add a sample app.** A Spring Boot 2.7 app with passing tests in a new folder, plus an `endpoints.json` (see `agent/securitydiff.py`) so the security equivalence check covers it. Add it to the CI matrix in `.github/workflows/ci.yml`.
- **Add a model to the benchmark.** `python3 agent/bench.py --models <ollama-tag>` and open a PR with the updated `BENCHMARK.md` and `reports/benchmark/`. Say which hardware you ran on.
- **Add a held-out app.** An open-source Spring Boot 2.7 Maven app we did not write, with a pinned commit and licence in `agent/heldout/manifest.json` and an endpoint spec next to it. Freeze the cheat sheet before its first run and report the first results as they come out (see `agent/heldout/README.md`).
- **Fix the agent.** Add a unit test with the fix. Keep the standard-library-only rule.

## Rules that keep the results honest

- The agent must never edit test files. If you change `write_source`, keep the guard and its tests.
- Do not tune the agent against one sample app only. If you add a hint that makes a model pass, say so in the PR, and add it to the README's description of what the harness provides.
- Never weaken the integrity checks (baseline test count, hashed test and build files, no test-skipping settings) to make a run pass.
- Report failures as they are. A run that is flagged for a human is a valid result.
