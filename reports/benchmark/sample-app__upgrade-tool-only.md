# Migration report

- App: `sample-app`  |  Model: none (upgrade tool only)  |  Upgrade tool: built-in fallback
- Spring Boot parent after upgrade: `3.3.5`
- Result: **NEEDS HUMAN REVIEW (tests failing)**
- Model fix rounds: 0 (max 0)

## Build score per run

Score = failing tests, or 1000+ compile errors. 0 means green. A run that scores worse than the best so far is rolled back.

| Run | Score | Tests passed | What happened |
|---|---|---|---|
| 1 | 1007 | - | build |

## Test integrity

Existing test files are never written by the agent; their hashes are checked after the upgrade tool runs and again at the end. Result: unchanged.

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

```

## Last build error (best state)
```
[ERROR] COMPILATION ERROR : 
[ERROR] <project>/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[9,72] cannot find symbol
[ERROR] <project>/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[15,37] cannot find symbol
[ERROR] <project>/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[22,5] method does not override or implement a method from a supertype
[ERROR] <project>/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[31,5] method does not override or implement a method from a supertype
[ERROR] <project>/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[33,16] cannot find symbol
[ERROR] <project>/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[36,5] method does not override or implement a method from a supertype
[ERROR] <project>/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[40,17] cannot find symbol
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.13.0:compile (default-compile) on project demo: Compilation failure: Compilation failure: 
[ERROR] <project>/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[9,72] cannot find symbol
[ERROR]   symbol:   class WebSecurityConfigurerAdapter
[ERROR]   location: package org.springframework.security.config.annotation.web.configuration
[ERROR] <project>/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[15,37] cannot find symbol
[ERROR]   symbol: class WebSecurityConfigurerAdapter
[ERROR] <project>/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[22,5] method does not override or implement a method from a supertype
[ERROR] <project>/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[31,5] method does not override or implement a method from a supertype
[ERROR] <project>/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[33,16] cannot find symbol
[ERROR]   symbol:   variable super
[ERROR]   location: class com.example.demo.SecurityConfig
[ERROR] <project>/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[36,5] method does not override or implement a method from a supertype
[ERROR] <project>/migrated-sample-app__upgrade-tool-only/src/main/java/com/example/demo/SecurityConfig.java:[40,17] cannot find symbol
[ERROR]   symbol:   method antMatchers(java.lang.String)
[ERROR]   location: class o
```