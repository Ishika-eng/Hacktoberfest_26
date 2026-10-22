# Migration report

- App: `sample-app`  |  Model: `qwen2.5-coder:7b-instruct`  |  Upgrade tool: OpenRewrite (rewrite-spring 6.37.1)
- Spring Boot parent after upgrade: `3.3.13`
- Result: **tests PASS**
- Model fix rounds: 1 (max 5)
- Settings: temperature 0, seed 0, 8192-token context; output fingerprint `44ec40c9a34f` (identical fingerprints across runs mean identical generated code)

## Build score per run

Score = failing tests, or 1000+ compile errors. 0 means green. A run that scores worse than the best so far is rolled back.

| Run | Score | Tests passed | What happened |
|---|---|---|---|
| 1 | 1006 | - | build; model fixed SecurityConfig.java |
| 2 | 1002 | - | build; auto-import fix in SecurityConfig.java |
| 3 | 0 | all | build |

## Test integrity

- Existing files under `src/test` (tests and test resources) and every `pom.xml` / `.mvn` file are hashed after the upgrade tool runs and again at the end. The fix loop can only write under `src/main`.
- The upgraded pom must not gain test-skipping settings (`skipTests`, `maven.test.skip`, `testFailureIgnore`, surefire `skip` or excludes).
- A passing run must execute exactly the baseline's tests: the original app ran 11 tests, 11 passed.
- Result: no violations.

## Security equivalence (same requests, Boot 2 build vs upgraded build)

18 checks, **0 difference(s)**, of which **0 newly accessible**. Cells show the HTTP status; changed cells show before → after. 401/403 means denied; 404 means the route was not found, which is a different problem.

| Endpoint | anonymous | user | admin |
|---|---|---|---|
| `GET /admin/` | 401 | 403 | 404 |
| `GET /admin/secret` | 401 | 403 | 200 |
| `GET /orders` | 401 | 405 | 405 |
| `GET /public/ping` | 200 | 200 | 200 |
| `POST /orders` | 401 | 400 | 400 |
| `POST /public/auth-check` | 401 | 401 | 401 |

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
@@ -1,4 +1,8 @@
 package com.example.demo;
+
+import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
+
+import static org.springframework.security.config.Customizer.withDefaults;
 
 import org.springframework.context.annotation.Bean;
 import org.springframework.context.annotation.Configuration;
@@ -6,41 +10,43 @@
 import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
 import org.springframework.security.config.annotation.web.builders.HttpSecurity;
 import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
-import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
 import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
 import org.springframework.security.crypto.password.PasswordEncoder;
+import org.springframework.security.core.userdetails.User;
+import org.springframework.security.core.userdetails.UserDetailsService;
+import org.springframework.security.provisioning.InMemoryUserDetailsManager;
+import org.springframework.security.web.SecurityFilterChain;
 
 @Configuration
 @EnableWebSecurity
-public class SecurityConfig extends WebSecurityConfigurerAdapter {
+public class SecurityConfig {
 
     @Bean
     public PasswordEncoder passwordEncoder() {
         return new BCryptPasswordEncoder();
     }
 
-    @Override
-    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
-        auth.inMemoryAuthentication()
-            .withUser("admin").password(passwordEncoder().encode("admin123")).roles("ADMIN")
-            .and()
-            .withUser("alice").password(passwordEncoder().encode("alice123")).roles("USER");
+    @Bean
+    public UserDetailsService userDetailsService(PasswordEncoder encoder) {
+        return new InMemoryUserDetailsManager(
+            User.withUsername("admin").password(encoder.encode("admin123")).roles("ADMIN").build(),
+            User.withUsername("alice").password(encoder.encode("alice123")).roles("USER").build()
+        );
     }
 
     @Bean
-    @Override
-    public AuthenticationManager authenticationManagerBean() throws Exception {
-        return super.authenticationManagerBean();
+    public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
+        return config.getAuthenticationManager();
     }
 
-    @Override
-    protected void configure(HttpSecurity http) throws Exception {
-        http.csrf().disable()
-            .authorizeRequests()
-                .antMatchers("/public/**").permitAll()
-                .antMatchers("/admin/**").hasRole("ADMIN")
-                .anyRequest().authenticated()
-            .and()
-            .httpBasic();
+    @Bean
+    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
+        http.csrf(csrf -> csrf.disable())
+            .authorizeHttpRequests(requests -> requests
+                .requestMatchers("/public/**").permitAll()
+                .requestMatchers("/admin/**").hasRole("ADMIN")
+                .anyRequest().authenticated())
+            .httpBasic(withDefaults());
+        return http.build();
     }
 }

```