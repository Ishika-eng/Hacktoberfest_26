# Migration report

- App: `sample-app`  |  Model: `qwen2.5-coder:7b-instruct`  |  Upgrade tool: built-in fallback
- Spring Boot parent after upgrade: `3.3.5`
- Result: **tests PASS**
- Model fix rounds: 2 (max 5)

## Build score per run

Score = failing tests, or 1000+ compile errors. 0 means green. A run that scores worse than the best so far is rolled back.

| Run | Score | Tests passed | What happened |
|---|---|---|---|
| 1 | 1007 | - | build; model fixed SecurityConfig.java |
| 2 | 1003 | - | build; auto-import fix in SecurityConfig.java |
| 3 | 1001 | - | build; model fixed SecurityConfig.java |
| 4 | 1001 | - | build; auto-import fix in SecurityConfig.java |
| 5 | 0 | all | build |

## Test integrity

Existing test files are never written by the agent; their hashes are checked after the upgrade tool runs and again at the end. Result: unchanged.

## Security equivalence (same requests, Boot 2 build vs upgraded build)

18 checks, **0 difference(s)**. Cells show the HTTP status; changed cells show before → after.

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
@@ -1,46 +1,54 @@
 package com.example.demo;
+
+import org.springframework.security.authentication.AuthenticationManager;
+
+import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
+import org.springframework.security.config.annotation.web.builders.HttpSecurity;
+import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
+import org.springframework.security.config.annotation.web.configurers.CsrfConfigurer;
+import org.springframework.security.config.annotation.web.configurers.HttpBasicConfigurer;
+import org.springframework.security.core.userdetails.User;
+import org.springframework.security.core.userdetails.UserDetailsService;
+import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
+import org.springframework.security.crypto.password.PasswordEncoder;
+import org.springframework.security.provisioning.InMemoryUserDetailsManager;
+import org.springframework.security.web.SecurityFilterChain;
 
 import org.springframework.context.annotation.Bean;
 import org.springframework.context.annotation.Configuration;
-import org.springframework.security.authentication.AuthenticationManager;
-import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
-import org.springframework.security.config.annotation.web.builders.HttpSecurity;
-import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
-import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
-import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
-import org.springframework.security.crypto.password.PasswordEncoder;
+import org.springframework.security.config.Customizer;
 
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
+    @Bean
+    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
+        http.csrf(csrf -> csrf.disable())
+            .authorizeHttpRequests(auth -> auth
+                .requestMatchers("/public/**").permitAll()
+                .requestMatchers("/admin/**").hasRole("ADMIN")
                 .anyRequest().authenticated()
-            .and()
-            .httpBasic();
+            )
+            .httpBasic(Customizer.withDefaults());
+        return http.build();
     }
 }

```