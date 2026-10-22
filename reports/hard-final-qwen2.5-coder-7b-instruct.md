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
@@ -1,4 +1,8 @@
 package com.example.demo;
+
+import org.springframework.security.config.Customizer;
+
+import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
 
 import org.springframework.context.annotation.Bean;
 import org.springframework.context.annotation.Configuration;
@@ -6,41 +10,44 @@
 import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
 import org.springframework.security.config.annotation.web.builders.HttpSecurity;
 import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
-import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
+import org.springframework.security.core.userdetails.User;
+import org.springframework.security.core.userdetails.UserDetailsService;
 import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
 import org.springframework.security.crypto.password.PasswordEncoder;
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