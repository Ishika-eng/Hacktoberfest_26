# Migration report

- App: `sample-jpa-app`  |  Model: `qwen2.5-coder:7b-instruct`  |  Upgrade tool: OpenRewrite (rewrite-spring 6.37.1)
- Spring Boot parent after upgrade: `3.3.13`
- Result: **tests PASS**
- Model fix rounds: 1 (max 5)
- Settings: temperature 0, seed 0, 8192-token context; output fingerprint `d0ac5c0e9568` (identical fingerprints across runs mean identical generated code)

## Build score per run

Score = failing tests, or 1000+ compile errors. 0 means green. A run that scores worse than the best so far is rolled back.

| Run | Score | Tests passed | What happened |
|---|---|---|---|
| 1 | 1001 | - | build; auto-repaired imports/@Override in SecurityConfig.java; model fixed Product.java |
| 2 | 0 | all | build; auto-repaired imports/@Override in Product.java |

## Test integrity

- Existing files under `src/test` (tests and test resources) and every `pom.xml` / `.mvn` file are hashed after the upgrade tool runs and again at the end. The fix loop can only write under `src/main`.
- The upgraded pom must not gain test-skipping settings (`skipTests`, `maven.test.skip`, `testFailureIgnore`, surefire `skip` or excludes).
- A passing run must execute exactly the baseline's tests: the original app ran 8 tests, 8 passed.
- Result: no violations.

## Security equivalence (same requests, Boot 2 build vs upgraded build)

24 checks, **2 difference(s)**, of which **0 newly accessible**. Cells show the HTTP status; changed cells show before → after. 401/403 means denied; 404 means the route was not found, which is a different problem.

| Endpoint | anonymous | clerk | manager |
|---|---|---|---|
| `DELETE /products/1` | 401 | 403 | 200 |
| `GET /actuator/health` | 200 | 200 | 200 |
| `GET /actuator/info` | 401 | 403 | 200 |
| `GET /products` | 401 | 200 | 200 |
| `GET /products/` | 401 | **200 → 404** | **200 → 404** |
| `GET /products/1` | 401 | 200 | 200 |
| `GET /whoami` | 200 | 200 | 200 |
| `POST /products` | 401 | 201 | 201 |

### What changed

| Request | Role | Before | After | What it means |
|---|---|---|---|---|
| `GET /products/` | clerk | 200 | 404 | the route no longer matches; not an access-control change, but clients will break |
| `GET /products/` | manager | 200 | 404 | the route no longer matches; not an access-control change, but clients will break |

**Flagged for a human: the upgraded app answers some requests differently. Review each before deploying.**

## Diff (all changes to Java sources, including the upgrade tool's)
```diff
--- a/Product.java
+++ b/Product.java
@@ -1,12 +1,13 @@
 package com.example.shop;
 
+import jakarta.persistence.Column;
+
 import java.math.BigDecimal;
-import javax.persistence.Entity;
-import javax.persistence.GeneratedValue;
-import javax.persistence.GenerationType;
-import javax.persistence.Id;
-import javax.validation.constraints.NotBlank;
-import org.hibernate.annotations.Type;
+import jakarta.persistence.Entity;
+import jakarta.persistence.GeneratedValue;
+import jakarta.persistence.GenerationType;
+import jakarta.persistence.Id;
+import jakarta.validation.constraints.NotBlank;
 
 @Entity
 public class Product {
@@ -21,7 +22,7 @@
     private BigDecimal price;
 
     // long free text: a plain String column would be limited to 255 characters
-    @Type(type = "text")
+    @Column(length = 10000)
     private String description;
 
     public Long getId() { return id; }

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

--- a/SecurityConfig.java
+++ b/SecurityConfig.java
@@ -1,20 +1,22 @@
 package com.example.shop;
+
+import static org.springframework.security.config.Customizer.withDefaults;
 
 import org.springframework.context.annotation.Bean;
 import org.springframework.context.annotation.Configuration;
 import org.springframework.http.HttpMethod;
 import org.springframework.security.config.annotation.web.builders.HttpSecurity;
 import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
-import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
 import org.springframework.security.core.userdetails.User;
 import org.springframework.security.core.userdetails.UserDetailsService;
 import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
 import org.springframework.security.crypto.password.PasswordEncoder;
 import org.springframework.security.provisioning.InMemoryUserDetailsManager;
+import org.springframework.security.web.SecurityFilterChain;
 
 @Configuration
 @EnableWebSecurity
-public class SecurityConfig extends WebSecurityConfigurerAdapter {
+public class SecurityConfig {
 
     @Bean
     public PasswordEncoder passwordEncoder() {
@@ -22,24 +24,22 @@
     }
 
     @Bean
-    @Override
     public UserDetailsService userDetailsService() {
         return new InMemoryUserDetailsManager(
             User.withUsername("clerk").password(passwordEncoder().encode("clerk123")).roles("CLERK").build(),
             User.withUsername("manager").password(passwordEncoder().encode("manager123")).roles("MANAGER").build());
     }
 
-    @Override
-    protected void configure(HttpSecurity http) throws Exception {
-        http.csrf().disable()
-            .authorizeRequests()
-                .antMatchers("/actuator/health").permitAll()
-                .antMatchers("/whoami").permitAll()
-                .antMatchers(HttpMethod.POST, "/products").hasAnyRole("CLERK", "MANAGER")
-                .antMatchers(HttpMethod.DELETE, "/products/**").hasRole("MANAGER")
-                .antMatchers("/actuator/**").hasRole("MANAGER")
-                .anyRequest().authenticated()
-            .and()
-            .httpBasic();
+    @Bean SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
+        http.csrf(csrf -> csrf.disable())
+                .authorizeHttpRequests(requests -> requests
+                        .requestMatchers("/actuator/health").permitAll()
+                        .requestMatchers("/whoami").permitAll()
+                        .requestMatchers(HttpMethod.POST, "/products").hasAnyRole("CLERK", "MANAGER")
+                        .requestMatchers(HttpMethod.DELETE, "/products/**").hasRole("MANAGER")
+                        .requestMatchers("/actuator/**").hasRole("MANAGER")
+                        .anyRequest().authenticated())
+                .httpBasic(withDefaults());
+        return http.build();
     }
 }

```

## Diagnosis (written by the model; unverified, check before relying on it)

The most likely cause of the HTTP status code changes after upgrading to Spring Boot 3 is the removal of `WebSecurityConfigurerAdapter` and the changes in the security configuration syntax. Developers need to act by updating their security configuration to use the new `SecurityFilterChain` bean and the `authorizeHttpRequests` method instead of `authorizeRequests`. This involves modifying the security configuration class to extend `Configuration` and `EnableWebSecurity`, and replacing the deprecated methods with their new equivalents.