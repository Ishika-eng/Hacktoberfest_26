# Boot Upgrade Agent

An agent that upgrades a **Spring Boot 2.7** app to **Spring Boot 3** using a small **open-weight** model running locally, and proves the result by running the app's own test suite.

Built for the *Best Open-Source AI Project* challenge at Hacktoberfest 2026 (project type: **model harness**).

## The problem

Spring Boot 2.x no longer gets open-source security fixes, but upgrading to 3.x is a breaking change: `javax.*` becomes `jakarta.*`, and APIs such as `WebSecurityConfigurerAdapter` are removed, so the Spring Security configuration has to be rewritten. Mechanical tools handle part of this. Engineers still fix the leftovers by hand, which is why the upgrade keeps getting postponed.

## What it does

```
Spring Boot 2.7 app
   │
   ▼  1. mechanical upgrade (parent version bump, javax -> jakarta)
   ▼  2. mvn test
   │        ├─ passes ──► write report
   │        └─ fails
   ▼  3. send the error + the broken file + a short migration cheat sheet
   │     to an open-weight model (via Ollama, on your machine)
   ▼  4. write the model's fixed file, go back to 2 (max 3 fix rounds)
   ▼
   Report: diff, test result, and anything left for a human
```

The model only ever sees the failing file and the error, not the whole repo. Company code never leaves the machine, which is the point of using an open-weight model.

The mechanical step in `agent/migrate.py` is a small stand-in for [OpenRewrite](https://docs.openrewrite.org/), which has official Spring Boot 3 recipes. Swapping it in is the obvious next step.

## Models used

| Model | Run through | Model card (licence and terms) |
|---|---|---|
| Qwen2.5-Coder 7B Instruct (`qwen2.5-coder:7b-instruct`) | Ollama | https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct |
| DeepSeek-Coder 6.7B (`deepseek-coder:6.7b`) | Ollama | https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-instruct |

Check each model card for its licence terms before reusing the weights. The model is a setting (`MODEL=...`), and any OpenAI-compatible endpoint can be used instead with `OPENAI_BASE_URL`.

## Results

Each case is the sample app in [`sample-app/`](sample-app), upgraded to Spring Boot 3.3.5. Reports are in [`reports/`](reports). All runs were on one laptop (18 GB RAM) with a single run per model, so treat them as indicative, not a benchmark.

**Case 1: security config only** (6 tests)

| Model | Tests after migration | Fix rounds | Time |
|---|---|---|---|
| Qwen2.5-Coder 7B | 6/6 pass | 2 | 26 s |
| DeepSeek-Coder 6.7B | 6/6 pass | 2 | 49 s |

Both rewrote `WebSecurityConfigurerAdapter` into a `SecurityFilterChain` bean. DeepSeek also modernised the `csrf` call; Qwen left the deprecated form, which still works.

**Case 2: harder, adds in-memory users, a `PasswordEncoder` and an exposed `AuthenticationManager` bean** (11 tests, with real login checks)

| Model | Run | Tests after migration | Outcome |
|---|---|---|---|
| Qwen2.5-Coder 7B | first run | 9/11 | Failed with `StackOverflowError`; stopped early |
| DeepSeek-Coder 6.7B | first run | 0/11 | Spring context failed to start; stopped early |
| Qwen2.5-Coder 7B | rerun with retry fallback, 3 fix rounds | 9/11 | Still `StackOverflowError`; flagged for a human |
| DeepSeek-Coder 6.7B | rerun with retry fallback | not yet recorded | |

In the first run the agent stopped before using its retries: Maven trims stack traces, so it could not tell which file to send back to the model. It now retries the files the model already edited. Even with that fix, neither 7B model solved the harder case on its own. The agent reports this honestly and leaves the failing files for a person.

## Limits

- Passing tests only proves what the tests cover.
- 6–7B models handle the common Spring Security rewrite but struggle with interacting changes (the harder case).
- The cheat sheet in [`agent/cheatsheet.md`](agent/cheatsheet.md) only covers the security-config change; Case 2 deliberately has no entries for its extra patterns.
- Only tested on the included sample app.

## Run it

You need Java 17+, Maven, Python 3 (standard library only) and [Ollama](https://docs.ollama.com/quickstart).

```bash
ollama pull qwen2.5-coder:7b-instruct

# baseline: the Spring Boot 2.7 sample app passes its tests
(cd sample-app && mvn test)

# run the agent (copies sample-app to migrated-app/, writes REPORT.md)
python3 agent/migrate.py

# try another model
MODEL=deepseek-coder:6.7b python3 agent/migrate.py
```

If `mvn` is not on your PATH, set `MVN=/path/to/mvn`. Other settings: `MAX_ATTEMPTS` (default 3), `BOOT3_VERSION` (default 3.3.5), `OLLAMA_URL`, and `OPENAI_BASE_URL` / `API_KEY` for a hosted open-weight model.

## Layout

| Path | What it is |
|---|---|
| `agent/migrate.py` | The agent: upgrade, build, model fix, retry, report |
| `agent/cheatsheet.md` | Migration notes given to the model |
| `sample-app/` | Spring Boot 2.7 app with security and validation tests |
| `reports/` | Reports from the model runs above |

## Licence

MIT, see [LICENSE](LICENSE).
