# Held-out apps

Apps we did **not** write, used to check that the agent and its cheat sheet are not tuned to our own two sample apps.

| App | Pinned commit | Licence | Notes |
|---|---|---|---|
| [spring-petclinic](https://github.com/spring-projects/spring-petclinic) | `a5cbb8505a1df3c348c06607933a07fc8c87c222` (2022-10-16, Spring Boot 2.7.3) | Apache-2.0 | JPA, Thymeleaf, caching, Actuator. **No Spring Security**, so the security check only covers anonymous access. |

| [spring-petclinic-rest](https://github.com/spring-petclinic/spring-petclinic-rest) | `b29ae4b88424301fe6b2236c6ee2cd71cc30cbf4` (2022-09-07, Spring Boot 2.6.2) | Apache-2.0 | Spring Security and Java code generated from an OpenAPI file at build time. Added after the first app stopped being held-out. |

**Status.** spring-petclinic: the first run failed (genuinely held-out); a later run passes after the agent was changed to ignore Gradle files, so that result is **not** held-out. spring-petclinic-rest: run once, untuned, and it fails because the generated sources use `javax.*` (the fix is in the pom, not in editable Java). See the main README.

The apps are not vendored. Fetch them at the pinned commit:

```bash
python3 agent/heldout.py            # clones into heldout/ (ignored by git)
python3 agent/migrate.py heldout/spring-petclinic --endpoints agent/heldout/spring-petclinic.endpoints.json
```

## Rules that keep it held-out

1. The cheat sheet is **frozen** before the first run on a held-out app. The commit it was frozen at is recorded in `BENCHMARK.md`.
2. Results are reported as they come out, including failures. They are not retried until they pass.
3. If the agent or cheat sheet is changed afterwards because of what a held-out run showed, that app is no longer held-out for the new version, and the result must be labelled that way.
