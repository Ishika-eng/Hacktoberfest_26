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
   ▼  3. missing import? fix it deterministically (like an IDE auto-import)
   ▼  4. otherwise send the error, the broken file, the ORIGINAL file, the source
   │     of the failing tests and a migration cheat sheet to an open-weight
   │     model (via Ollama, on your machine)
   ▼  5. write the model's fixed file, go back to 2 (max 5 fix rounds)
   ▼
   Report: diff, test result, and anything left for a human
```

The model only ever sees the failing file, its original version, the error and the failing tests, never the whole repo. Company code never leaves the machine, which is the point of using an open-weight model.

The mechanical step in `agent/migrate.py` is a small stand-in for [OpenRewrite](https://docs.openrewrite.org/), which has official Spring Boot 3 recipes. Swapping it in is the obvious next step.

## Models used

| Model | Run through | Licence | Model card |
|---|---|---|---|
| Qwen2.5-Coder 7B Instruct (`qwen2.5-coder:7b-instruct`) | Ollama | [Apache 2.0](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct/blob/main/LICENSE) (open source) | [Hugging Face](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct) |
| DeepSeek-Coder 6.7B (`deepseek-coder:6.7b`) | Ollama | [DeepSeek License Agreement v1.0](https://github.com/deepseek-ai/deepseek-coder/blob/main/LICENSE-MODEL) (open-weight, not open source) | [Hugging Face](https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-instruct) |

- **Qwen2.5-Coder** is under the standard Apache 2.0 licence: commercial use and redistribution are allowed with the usual notices.
- **DeepSeek-Coder** is open-weight under a custom licence. Commercial use is allowed, but the licence has use restrictions (for example no military use and no harmful or fully automated decisions) that must be passed on to anyone you redistribute the model or derivatives to. It is governed by PRC law.
- Licence details were read from the model cards on 22 Oct 2026 (card pages and licence texts); re-check them before redistributing weights. The cards describe the Hugging Face Instruct models; we run the Ollama tags above and have not checked that they are byte-identical to those releases.

The model is a setting (`MODEL=...`), and any OpenAI-compatible endpoint can be used instead with `OPENAI_BASE_URL`.

## Results

Each case is the sample app in [`sample-app/`](sample-app), upgraded to Spring Boot 3.3.5. Reports are in [`reports/`](reports). All runs were on one laptop (18 GB RAM) with a single run per model, so treat them as indicative, not a benchmark.

**Case 1: security config only** (6 tests)

| Model | Tests after migration | Fix rounds | Time |
|---|---|---|---|
| Qwen2.5-Coder 7B | 6/6 pass | 2 | 26 s |
| DeepSeek-Coder 6.7B | 6/6 pass | 2 | 49 s |

Both rewrote `WebSecurityConfigurerAdapter` into a `SecurityFilterChain` bean. DeepSeek also modernised the `csrf` call; Qwen left the deprecated form, which still works.

**Case 2: harder, adds in-memory users, a `PasswordEncoder` and an exposed `AuthenticationManager` bean** (11 tests, with real login checks)

This is what the sample app in [`sample-app/`](sample-app) contains now. Case 1 above was run on an earlier, smaller version of it (6 tests), so it can no longer be reproduced with this repo.

| Model | Tests after migration | Outcome |
|---|---|---|
| Qwen2.5-Coder 7B | **11/11 pass** | 1 model round + 1 automatic import repair, about 30 s. Reproduced in 2 runs. |
| DeepSeek-Coder 6.7B | 8/11 | Compiles but disables HTTP Basic (`httpBasic(AbstractHttpConfigurer::disable)`) where the original enabled it, so 3 login tests fail. Same result in repeated runs; flagged for a human. |

How the harder case got to this point, so the numbers are not misread: the first runs (see `reports/hard-first-run-*` and `reports/hard-rerun-*`) failed for both models. Qwen reached 9/11 with a `StackOverflowError`, and DeepSeek did not compile. We then added help to the harness, and Qwen passes with it:

- cheat sheet entries for the Spring Security 6 user store and `AuthenticationManager` bean, and for the correct import packages
- the original Spring Boot 2.7 file and the source of the failing tests in the prompt
- an automatic import repair for known Spring Security classes, before the model is asked
- 5 fix rounds instead of 3, an 8192-token context, and a 30-second per-test timeout

So the honest reading is: **Qwen passes inside a harness that supplies this knowledge; it did not work it out unaided.** DeepSeek did not pass even with the same help. Trying randomness on retries did not help it (and made it much slower), so that was removed.

## Limits

- Passing tests only proves what the tests cover.
- 6–7B models handle the common Spring Security rewrite but struggle with interacting changes. One of the two models failed the harder case.
- The cheat sheet and the import table in the agent are written for Spring Security 6. Supporting other migrations means extending them.
- Case 2's cheat sheet was extended after seeing the models fail on this sample app, so its pass is not a measure of generalisation. Only tested on the included sample app.

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

If `mvn` is not on your PATH, set `MVN=/path/to/mvn`. Other settings: `MAX_ATTEMPTS` (default 5), `BOOT3_VERSION` (default 3.3.5), `OLLAMA_URL`, and `OPENAI_BASE_URL` / `API_KEY` for a hosted open-weight model.

## Layout

| Path | What it is |
|---|---|
| `agent/migrate.py` | The agent: upgrade, build, model fix, retry, report |
| `agent/cheatsheet.md` | Migration notes given to the model |
| `sample-app/` | Spring Boot 2.7 app with security and validation tests |
| `reports/` | Reports from the model runs above |

## Licence

MIT, see [LICENSE](LICENSE).
