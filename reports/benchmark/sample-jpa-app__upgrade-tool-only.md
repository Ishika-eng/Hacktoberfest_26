# Migration report

- App: `sample-jpa-app`  |  Model: none (upgrade tool only)  |  Upgrade tool: built-in fallback
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
--- a/Product.java
+++ b/Product.java
@@ -1,11 +1,11 @@
 package com.example.shop;
 
 import java.math.BigDecimal;
-import javax.persistence.Entity;
-import javax.persistence.GeneratedValue;
-import javax.persistence.GenerationType;
-import javax.persistence.Id;
-import javax.validation.constraints.NotBlank;
+import jakarta.persistence.Entity;
+import jakarta.persistence.GeneratedValue;
+import jakarta.persistence.GenerationType;
+import jakarta.persistence.Id;
+import jakarta.validation.constraints.NotBlank;
 import org.hibernate.annotations.Type;
 
 @Entity

--- a/ProductController.java
+++ b/ProductController.java
@@ -1,8 +1,8 @@
 package com.example.shop;
 
 import java.util.List;
-import javax.servlet.http.HttpServletRequest;
-import javax.validation.Valid;
+import jakarta.servlet.http.HttpServletRequest;
+import jakarta.validation.Valid;
 import org.springframework.http.HttpStatus;
 import org.springframework.web.bind.annotation.*;
 import org.springframework.web.server.ResponseStatusException;

```

## Last build error (best state)
```
[ERROR] COMPILATION ERROR : 
[ERROR] <project>/migrated-sample-jpa-app__upgrade-tool-only/src/main/java/com/example/shop/SecurityConfig.java:[8,72] cannot find symbol
[ERROR] <project>/migrated-sample-jpa-app__upgrade-tool-only/src/main/java/com/example/shop/SecurityConfig.java:[17,37] cannot find symbol
[ERROR] <project>/migrated-sample-jpa-app__upgrade-tool-only/src/main/java/com/example/shop/Product.java:[24,11] cannot find symbol
[ERROR] <project>/migrated-sample-jpa-app__upgrade-tool-only/src/main/java/com/example/shop/Product.java:[24,5] annotation @org.hibernate.annotations.Type is missing a default value for the element 'value'
[ERROR] <project>/migrated-sample-jpa-app__upgrade-tool-only/src/main/java/com/example/shop/SecurityConfig.java:[25,5] method does not override or implement a method from a supertype
[ERROR] <project>/migrated-sample-jpa-app__upgrade-tool-only/src/main/java/com/example/shop/SecurityConfig.java:[32,5] method does not override or implement a method from a supertype
[ERROR] <project>/migrated-sample-jpa-app__upgrade-tool-only/src/main/java/com/example/shop/SecurityConfig.java:[36,17] cannot find symbol
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.13.0:compile (default-compile) on project shop: Compilation failure: Compilation failure: 
[ERROR] <project>/migrated-sample-jpa-app__upgrade-tool-only/src/main/java/com/example/shop/SecurityConfig.java:[8,72] cannot find symbol
[ERROR]   symbol:   class WebSecurityConfigurerAdapter
[ERROR]   location: package org.springframework.security.config.annotation.web.configuration
[ERROR] <project>/migrated-sample-jpa-app__upgrade-tool-only/src/main/java/com/example/shop/SecurityConfig.java:[17,37] cannot find symbol
[ERROR]   symbol: class WebSecurityConfigurerAdapter
[ERROR] <project>/migrated-sample-jpa-app__upgrade-tool-only/src/main/java/com/example/shop/Product.java:[24,11] cannot find symbol
[ERROR]   symbol:   method type()
[ERROR]   location: @interface org.hibernate.annotations.Type
[ERROR] <project>/migrated-sample-jpa-app__upgrade-tool-only/src/main/java/com/example/shop/Product.java:[24,5] annotation @org.hibernate.annotations.Type is missing a default value for the element 'value'
[ERROR] <project>/migrated-sample-jpa-app__upgrade-tool-only/src/main/java/com/example/shop/SecurityConfig.java:[25,5] method does not override or implement a method from a supertype
[ERROR] <project>/migrated-sample-jpa-app__upgrade-tool-only/src/main/java/com/example/shop/SecurityConfig.java:[32,5] method does not override or implement a method from a supertype
[ERROR] <project>/migrated-sample-jpa-app__upgrade-tool-only/src/main/java/com/example/shop/SecurityConfig.java:[36,17] cannot find 
```