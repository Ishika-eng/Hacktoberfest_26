# Migration report

- App: `sample-app`  |  Model: none (upgrade tool only)  |  Upgrade tool: OpenRewrite (rewrite-spring 6.37.1)
- Spring Boot parent after upgrade: `3.3.13`
- Result: **NEEDS HUMAN REVIEW (tests failing)**
- Model fix rounds: 0 (max 0)
- Settings: temperature 0, seed 0, 8192-token context; output fingerprint `a0c4ca7b5e47` (identical fingerprints across runs mean identical generated code)

## Build score per run

Score = failing tests, or 1000+ compile errors. 0 means green. A run that scores worse than the best so far is rolled back.

| Run | Score | Tests passed | What happened |
|---|---|---|---|
| 1 | 1006 | - | build |

## Test integrity

- Existing files under `src/test` (tests and test resources) and every `pom.xml` / `.mvn` file are hashed after the upgrade tool runs and again at the end. The fix loop can only write under `src/main`.
- The upgraded pom must not gain test-skipping settings (`skipTests`, `maven.test.skip`, `testFailureIgnore`, surefire `skip` or excludes).
- A passing run must execute exactly the baseline's tests: the original app ran 11 tests, 11 passed.
- Result: no violations.

## Diff (all changes to Java sources, including the upgrade tool's)
```diff
--- a/ApiController.java
+++ b/ApiController.java
@@ -1,6 +1,6 @@
 package com.example.demo;
 
-import javax.validation.Valid;
+import jakarta.validation.Valid;
 import org.springframework.web.bind.annotation.*;
 
 @RestController

--- a/Order.java
+++ b/Order.java
@@ -1,7 +1,7 @@
 package com.example.demo;
 
-import javax.validation.constraints.Min;
-import javax.validation.constraints.NotBlank;
+import jakarta.validation.constraints.Min;
+import jakarta.validation.constraints.NotBlank;
 
 public class Order {
     @NotBlank

--- a/SecurityConfig.java
+++ b/SecurityConfig.java
@@ -1,4 +1,6 @@
 package com.example.demo;
+
+import static org.springframework.security.config.Customizer.withDefaults;
 
 import org.springframework.context.annotation.Bean;
 import org.springframework.context.annotation.Configuration;
@@ -27,7 +29,7 @@
             .withUser("alice").password(passwordEncoder().encode("alice123")).roles("USER");
     }
 
-    @Bean
+    /*~~(Migrate manually based on https://spring.io/blog/2022/02/21/spring-security-without-the-websecurityconfigureradapter)~~>*/@Bean
     @Override
     public AuthenticationManager authenticationManagerBean() throws Exception {
         return super.authenticationManagerBean();
@@ -35,12 +37,11 @@
 
     @Override
     protected void configure(HttpSecurity http) throws Exception {
-        http.csrf().disable()
-            .authorizeRequests()
-                .antMatchers("/public/**").permitAll()
-                .antMatchers("/admin/**").hasRole("ADMIN")
-                .anyRequest().authenticated()
-            .and()
-            .httpBasic();
+        http.csrf(csrf -> csrf.disable())
+            .authorizeHttpRequests(requests -> requests
+                .requestMatchers("/public/**").permitAll()
+                .requestMatchers("/admin/**").hasRole("ADMIN")
+                .anyRequest().authenticated())
+            .httpBasic(withDefaults());
     }
 }

```

## Last build error (best state)
```
[ERROR] COMPILATION ERROR : 
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-bench/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[11,72] cannot find symbol
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-bench/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[17,37] cannot find symbol
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-bench/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[24,5] method does not override or implement a method from a supertype
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-bench/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[33,5] method does not override or implement a method from a supertype
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-bench/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[35,16] cannot find symbol
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-bench/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[38,5] method does not override or implement a method from a supertype
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.13.0:compile (default-compile) on project demo: Compilation failure: Compilation failure: 
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-bench/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[11,72] cannot find symbol
[ERROR]   symbol:   class WebSecurityConfigurerAdapter
[ERROR]   location: package org.springframework.security.config.annotation.web.configuration
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-bench/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[17,37] cannot find symbol
[ERROR]   symbol: class WebSecurityConfigurerAdapter
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-bench/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[24,5] method does not override or implement a method from a supertype
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-bench/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[33,5] method does not override or implement a method from a supertype
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-bench/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[35,16] cannot find symbol
[ERROR]   symbol:   variable super
[ERROR]   location: class com.example.demo.SecurityConfig
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-bench/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[38,5] method does not override or implement a method from a supertype
[ERROR] -> [Help 1]
[ERROR] 
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR] 
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.a
```