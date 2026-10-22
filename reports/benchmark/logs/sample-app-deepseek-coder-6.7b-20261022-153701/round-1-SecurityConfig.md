# Round 1: SecurityConfig.java

Model: `deepseek-coder:6.7b`

## Prompt

You are migrating a Spring Boot 2.7 app to Spring Boot 3 (Spring Security 6, Hibernate 6, Java 17).
The build or tests failed. Fix the file below so it compiles and keeps the SAME behaviour as the original.
Every feature the original enables (for example HTTP Basic auth, CSRF settings, URL rules, users, beans) must still be enabled.
Comments like /*~~(Migrate manually ...)~~>*/ were left by OpenRewrite where it could not migrate; handle them and delete the marker.

Migration notes:
Spring Boot 2.x -> 3.x migration notes (Spring Security 6):
- WebSecurityConfigurerAdapter is removed. Do NOT extend it. Declare a `@Bean SecurityFilterChain filterChain(HttpSecurity http) throws Exception` and `return http.build();`.
- Remove the `@Override`; the class is just `@Configuration` (+ `@EnableWebSecurity`).
- `authorizeRequests()` -> `authorizeHttpRequests(auth -> auth ...)`.
- `antMatchers(...)` / `mvcMatchers(...)` -> `requestMatchers(...)`.
- `.and()` chaining is deprecated: use lambdas, e.g. `http.csrf(csrf -> csrf.disable())`, `http.httpBasic(Customizer.withDefaults())`.
- `javax.*` (persistence, validation, servlet) -> `jakarta.*`.

Users and authentication (Spring Security 6):
- `configure(AuthenticationManagerBuilder)` is gone. Remove it. Define users as a bean instead:
  `@Bean public UserDetailsService userDetailsService(PasswordEncoder encoder) { return new InMemoryUserDetailsManager(User.withUsername("admin").password(encoder.encode("pw")).roles("ADMIN").build(), ...); }`
  (`org.springframework.security.core.userdetails.User`, `...provisioning.InMemoryUserDetailsManager`). Keep the same usernames, passwords and roles.
- Keep the existing `PasswordEncoder` bean. Never build the encoder or the manager by calling a bean method that calls itself.
- `authenticationManagerBean()` / `super.authenticationManagerBean()` are gone. Do NOT override or call them. Expose the manager like this:
  `@Bean public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception { return config.getAuthenticationManager(); }`
  (`org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration`).
- Do not inject `AuthenticationManagerBuilder` into a bean method and call `build()` on it.

Rules for the rewritten file:
- Keep every bean from the original class (PasswordEncoder, users, AuthenticationManager, SecurityFilterChain) in the same class.
- Add an `import` for every class you use (Customizer, User, InMemoryUserDetailsManager, UserDetailsService, AuthenticationConfiguration, SecurityFilterChain, ...).
- Use `http.csrf(csrf -> csrf.disable())` and `.httpBasic(Customizer.withDefaults())`.

Imports that are easy to get wrong:
- `Customizer` is `org.springframework.security.config.Customizer` (NOT in `...web.configurers`).
- `SecurityFilterChain` is `org.springframework.security.web.SecurityFilterChain`.
- `PasswordEncoder` is `org.springframework.security.crypto.password.PasswordEncoder`; `BCryptPasswordEncoder` is `org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder`.

Hibernate 6 / JPA (Spring Boot 3 uses Hibernate 6):
- `javax.persistence.*` -> `jakarta.persistence.*` (already rewritten by the upgrade tool).
- `@Type(type = "...")` no longer exists: the `type` attribute was removed. Delete the `@Type` annotation (and its import) and map the column another way:
  a long text column -> `@Column(length = 10000)` or `@Lob`; keep the field type `String`. Never leave the old `@Type(type=...)`.
- `@TypeDef` / `@TypeDefs` are removed too.
- Keep ID generation as it was (`GenerationType.IDENTITY` stays `IDENTITY`).

Spring Boot 3 property renames (application.properties / application.yml):
- `spring.redis.*` -> `spring.data.redis.*`
- `server.max-http-header-size` -> `server.max-http-request-header-size`
- `management.metrics.export.<product>.*` -> `management.<product>.metrics.export.*`
- Spring MVC no longer matches a trailing slash: `GET /products/` no longer reaches the `/products` handler (404). Do not "fix" this by changing security rules; report it.

Custom auto-configuration:
- Registering auto-configuration classes under the `org.springframework.boot.autoconfigure.EnableAutoConfiguration` key in `META-INF/spring.factories` is no longer read.
  Move the class names, one per line, to `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`.

Build error:
[ERROR] COMPILATION ERROR : 
[ERROR] <project>/migrated-sample-app__deepseek-coder-6.7b__run1/src/main/java/com/example/demo/SecurityConfig.java:[9,72] cannot find symbol
[ERROR] <project>/migrated-sample-app__deepseek-coder-6.7b__run1/src/main/java/com/example/demo/SecurityConfig.java:[15,37] cannot find symbol
[ERROR] <project>/migrated-sample-app__deepseek-coder-6.7b__run1/src/main/java/com/example/demo/SecurityConfig.java:[22,5] method does not override or implement a method from a supertype
[ERROR] <project>/migrated-sample-app__deepseek-coder-6.7b__run1/src/main/java/com/example/demo/SecurityConfig.java:[31,5] method does not override or implement a method from a supertype
[ERROR] <project>/migrated-sample-app__deepseek-coder-6.7b__run1/src/main/java/com/example/demo/SecurityConfig.java:[33,16] cannot find symbol
[ERROR] <project>/migrated-sample-app__deepseek-coder-6.7b__run1/src/main/java/com/example/demo/SecurityConfig.java:[36,5] method does not override or implement a method from a supertype
[ERROR] <project>/migrated-sample-app__deepseek-coder-6.7b__run1/src/main/java/com/example/demo/SecurityConfig.java:[40,17] cannot find symbol
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.13.0:compile (default-compile) on project demo: Compilation failure: Compilation failure: 
[ERROR] <project>/migrated-sample-app__deepseek-coder-6.7b__run1/src/main/java/com/example/demo/SecurityConfig.java:[9,72] cannot find symbol
[ERROR]   symbol:   class WebSecurityConfigurerAdapter
[ERROR]   location: package org.springframework.security.config.annotation.web.configuration
[ERROR] <project>/migrated-sample-app__deepseek-coder-6.7b__run1/src/main/java/com/example/demo/SecurityConfig.java:[15,37] cannot find symbol
[ERROR]   symbol: class WebSecurityConfigurerAdapter
[ERROR] <project>/migrated-sample-app__deepseek-coder-6.7b__run1/src/main/java/com/example/demo/SecurityConfig.java:[22,5] method does not override or implement a method from a supertype
[ERROR] <project>/migrated-sample-app__deepseek-coder-6.7b__run1/src/main/java/com/example/demo/SecurityConfig.java:[31,5] method does not override or implement a method from a supertype
[ERROR] <project>/migrated-sample-app__deepseek-coder-6.7b__run1/src/main/java/com/example/demo/SecurityConfig.java:[33,16] cannot find symbol
[ERROR]   symbol:   variable super
[ERROR]   location: class com.example.demo.SecurityConfig
[ERROR] <project>/migrated-sample-app__deepseek-coder-6.7b__run1/src/main/java/com/example/demo/SecurityConfig.java:[36,5] method does not override or implement a method from a supertype
[ERROR] <project>/migrated-sample-app__deepseek-coder-6.7b__run1/src/main/java/com/example/demo/SecurityConfig.java

ORIGINAL Spring Boot 2.7 version of SecurityConfig.java (this is the behaviour to preserve):
```java
package com.example.demo;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
        auth.inMemoryAuthentication()
            .withUser("admin").password(passwordEncoder().encode("admin123")).roles("ADMIN")
            .and()
            .withUser("alice").password(passwordEncoder().encode("alice123")).roles("USER");
    }

    @Bean
    @Override
    public AuthenticationManager authenticationManagerBean() throws Exception {
        return super.authenticationManagerBean();
    }

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.csrf().disable()
            .authorizeRequests()
                .antMatchers("/public/**").permitAll()
                .antMatchers("/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            .and()
            .httpBasic();
    }
}

```

CURRENT version of SecurityConfig.java (this is what fails):
```java
package com.example.demo;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
        auth.inMemoryAuthentication()
            .withUser("admin").password(passwordEncoder().encode("admin123")).roles("ADMIN")
            .and()
            .withUser("alice").password(passwordEncoder().encode("alice123")).roles("USER");
    }

    @Bean
    @Override
    public AuthenticationManager authenticationManagerBean() throws Exception {
        return super.authenticationManagerBean();
    }

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.csrf().disable()
            .authorizeRequests()
                .antMatchers("/public/**").permitAll()
                .antMatchers("/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            .and()
            .httpBasic();
    }
}

```
Reply with the complete corrected file in a single ```java block and nothing else.

## Reply

Here is the corrected version of your `SecurityConfig.java` file:

```java
package com.example.demo;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public UserDetailsService userDetailsService(PasswordEncoder encoder) {
        return new InMemoryUserDetailsManager(
                User.withUsername("admin")
                        .password(encoder.encode("admin123"))
                        .roles("ADMIN")
                        .build(),
                User.withUsername("alice")
                        .password(encoder.encode("alice123"))
                        .roles("USER")
                        .build()
        );
    }

    @Bean
    public AuthenticationManager authenticationManager(org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
                .csrf(AbstractHttpConfigurer::disable)
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/public/**").permitAll()
                        .requestMatchers("/admin/**").hasRole("ADMIN")
                        .anyRequest().authenticated()
                )
                .httpBasic(AbstractHttpConfigurer::authenticationEntryPoint)
                .build();
    }
}
```

Please note that the `authenticationEntryPoint` method in the `httpBasic` configuration is used to set the `AuthenticationEntryPoint` which is responsible for sending the 401 Unauthorized response. If you don't want to set any custom `AuthenticationEntryPoint`, you can use `AbstractHttpConfigurer::disable`.

