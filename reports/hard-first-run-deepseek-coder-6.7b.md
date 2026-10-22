# Migration report
- Model: `deepseek-coder:6.7b`
- Target: Spring Boot 3.3.5
- Result: **NEEDS HUMAN REVIEW (tests failing)**
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
@@ -6,41 +6,45 @@
 import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
 import org.springframework.security.config.annotation.web.builders.HttpSecurity;
 import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
-import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
+import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
 import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
 import org.springframework.security.crypto.password.PasswordEncoder;
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
+    @Bean
+    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
+        http.csrf(AbstractHttpConfigurer::disable)
+                .authorizeHttpRequests(auth -> auth
+                        .requestMatchers("/public/**").permitAll()
+                        .requestMatchers("/admin/**").hasRole("ADMIN")
+                        .anyRequest().authenticated()
+                )
+                .httpBasic();
+        return http.build();
+    }
+
     protected void configure(AuthenticationManagerBuilder auth) throws Exception {
         auth.inMemoryAuthentication()
-            .withUser("admin").password(passwordEncoder().encode("admin123")).roles("ADMIN")
-            .and()
-            .withUser("alice").password(passwordEncoder().encode("alice123")).roles("USER");
+                .withUser("admin").password(passwordEncoder().encode("admin123")).roles("ADMIN")
+                .and()
+                .withUser("alice").password(passwordEncoder().encode("alice123")).roles("USER");
     }
 
     @Bean
-    @Override
-    public AuthenticationManager authenticationManagerBean() throws Exception {
-        return super.authenticationManagerBean();
-    }
-
-    @Override
-    protected void configure(HttpSecurity http) throws Exception {
-        http.csrf().disable()
-            .authorizeRequests()
-                .antMatchers("/public/**").permitAll()
-                .antMatchers("/admin/**").hasRole("ADMIN")
-                .anyRequest().authenticated()
-            .and()
-            .httpBasic();
+    public AuthenticationManager authenticationManagerBean(AuthenticationManagerBuilder auth) throws Exception {
+        auth.inMemoryAuthentication()
+                .withUser("admin").password(passwordEncoder().encode("admin123")).roles("ADMIN")
+                .and()
+                .withUser("alice").password(passwordEncoder().encode("alice123")).roles("USER");
+        return auth.build();
     }
 }

```

## Last build error
```
2026-10-22T13:55:04.631+05:30 ERROR 61848 --- [           main] o.s.boot.SpringApplication               : Application run failed
Caused by: org.springframework.beans.factory.BeanCreationException: Error creating bean with name 'org.springframework.security.config.annotation.web.configuration.HttpSecurityConfiguration.httpSecurity' defined in class path resource [org/springframework/security/config/annotation/web/configuration/HttpSecurityConfiguration.class]: Failed to instantiate [org.springframework.security.config.annotation.web.builders.HttpSecurity]: Factory method 'httpSecurity' threw exception with message: Cannot apply org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration$EnableGlobalAuthenticationAutowiredConfigurer@237f7970 to already built object
Caused by: org.springframework.beans.BeanInstantiationException: Failed to instantiate [org.springframework.security.config.annotation.web.builders.HttpSecurity]: Factory method 'httpSecurity' threw exception with message: Cannot apply org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration$EnableGlobalAuthenticationAutowiredConfigurer@237f7970 to already built object
Caused by: java.lang.IllegalStateException: Cannot apply org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration$EnableGlobalAuthenticationAutowiredConfigurer@237f7970 to already built object
Caused by: org.springframework.beans.factory.UnsatisfiedDependencyException: Error creating bean with name 'org.springframework.security.config.annotation.web.configuration.WebSecurityConfiguration': Unsatisfied dependency expressed through field 'httpSecurity': Error creating bean with name 'org.springframework.security.config.annotation.web.configuration.HttpSecurityConfiguration.httpSecurity' defined in class path resource [org/springframework/security/config/annotation/web/configuration/HttpSecurityConfiguration.class]: Failed to instantiate [org.springframework.security.config.annotation.web.builders.HttpSecurity]: Factory method 'httpSecurity' threw exception with message: Cannot apply org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration$EnableGlobalAuthenticationAutowiredConfigurer@237f7970 to already built object
Caused by: org.springframework.beans.factory.BeanCreationException: Error creating bean with name 'org.springframework.security.config.annotation.web.configuration.HttpSecurityConfiguration.httpSecurity' defined in class path resource [org/springframework/security/config/annotation/web/configuration/HttpSecurityConfiguration.class]: Failed to instantiate [org.springframework.security.config.annotation.web.builders.HttpSecurity]: Factory method 'httpSecurity' threw exception with message: Cannot apply org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration$EnableGlobalAuthenticationAutowiredConfigurer@237f7970 to already built object
Caused by: org.springframework.beans.BeanInstantiationException: Failed to instantiate [org.springframework.security.config.annotation.web.builders.HttpSecurity]: Factory method 'httpSecurity' threw exception with message: Cannot apply org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration$EnableGlobalAuthenticationAutowiredConfigurer@237f7970 to already built object
Caused by: java.lang.IllegalSt
```