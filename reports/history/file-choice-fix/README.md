# DeepSeek-Coder after the file-choice fix (history)

Two runs of `deepseek-coder:6.7b` on `sample-jpa-app`, made with commit `98db3ac` ("Choose files to fix from the model's own edits when tests fail at runtime"), before the integrity checks and the held-out app were added.

Before that commit, DeepSeek spent all five model rounds editing `ShopApplication.java`, a file unrelated to the failure. With it, every round went to `SecurityConfig.java` and `Product.java`, the files the model had edited. The result did not improve: both runs ended at 3/8 tests, because DeepSeek wrote `.httpBasic(AbstractHttpConfigurer::disable)` (HTTP Basic switched off) in every round, even though the prompt showed the original file, the failing tests and the cheat sheet.

So the file-choice weakness is fixed, and DeepSeek's remaining failure here is the model's own. The final benchmark in `BENCHMARK.md` was rerun from scratch with the final code; these two runs are kept only as evidence of that step.
