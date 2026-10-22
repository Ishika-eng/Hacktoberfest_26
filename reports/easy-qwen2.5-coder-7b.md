# Migration report
- Model: `qwen2.5-coder:7b-instruct`
- Target: Spring Boot 3.3.5
- Result: **tests PASS**
- Model fix rounds: 2

## Diff
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
@@ -1,22 +1,25 @@
 package com.example.demo;
 
+import org.springframework.context.annotation.Bean;
 import org.springframework.context.annotation.Configuration;
 import org.springframework.security.config.annotation.web.builders.HttpSecurity;
 import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
-import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
+import org.springframework.security.web.SecurityFilterChain;
+import org.springframework.security.config.Customizer;
 
 @Configuration
 @EnableWebSecurity
-public class SecurityConfig extends WebSecurityConfigurerAdapter {
+public class SecurityConfig {
 
-    @Override
-    protected void configure(HttpSecurity http) throws Exception {
+    @Bean
+    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
         http.csrf().disable()
-            .authorizeRequests()
-                .antMatchers("/public/**").permitAll()
-                .antMatchers("/admin/**").hasRole("ADMIN")
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