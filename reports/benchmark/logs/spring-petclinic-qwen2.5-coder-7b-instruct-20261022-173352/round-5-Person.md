# Round 5: Person.java

Model: `qwen2.5-coder:7b-instruct`

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
[ERROR] [ERROR] Some problems were encountered while processing the POMs:
[ERROR] 'dependencies.dependency.version' for mysql:mysql-connector-java:jar is missing. @ line 70, column 17
[ERROR] The build could not read 1 project -> [Help 1]
[ERROR]   
[ERROR]   The project org.springframework.samples:spring-petclinic:2.7.3 (/private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-bench/migrated-heldout-spring-petclinic__qwen2.5-coder-7b-instruct__run1/pom.xml) has 1 error
[ERROR]     'dependencies.dependency.version' for mysql:mysql-connector-java:jar is missing. @ line 70, column 17
[ERROR] 
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR] 
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/ProjectBuildingException

ORIGINAL Spring Boot 2.7 version of Person.java (this is the behaviour to preserve):
```java
/*
 * Copyright 2012-2019 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.springframework.samples.petclinic.model;

import javax.persistence.Column;
import javax.persistence.MappedSuperclass;
import javax.validation.constraints.NotEmpty;

/**
 * Simple JavaBean domain object representing an person.
 *
 * @author Ken Krebs
 */
@MappedSuperclass
public class Person extends BaseEntity {

	@Column(name = "first_name")
	@NotEmpty
	private String firstName;

	@Column(name = "last_name")
	@NotEmpty
	private String lastName;

	public String getFirstName() {
		return this.firstName;
	}

	public void setFirstName(String firstName) {
		this.firstName = firstName;
	}

	public String getLastName() {
		return this.lastName;
	}

	public void setLastName(String lastName) {
		this.lastName = lastName;
	}

}

```

CURRENT version of Person.java (this is what fails):
```java
/*
 * Copyright 2012-2019 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.springframework.samples.petclinic.model;

import jakarta.persistence.Column;
import jakarta.persistence.MappedSuperclass;
import jakarta.validation.constraints.NotEmpty;

/**
 * Simple JavaBean domain object representing an person.
 *
 * @author Ken Krebs
 */
@MappedSuperclass
public class Person extends BaseEntity {

	@Column(name = "first_name")
	@NotEmpty
	private String firstName;

	@Column(name = "last_name")
	@NotEmpty
	private String lastName;

	public String getFirstName() {
		return this.firstName;
	}

	public void setFirstName(String firstName) {
		this.firstName = firstName;
	}

	public String getLastName() {
		return this.lastName;
	}

	public void setLastName(String lastName) {
		this.lastName = lastName;
	}

}

```
Reply with the complete corrected file in a single ```java block and nothing else.

## Reply

```java
/*
 * Copyright 2012-2019 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.springframework.samples.petclinic.model;

import jakarta.persistence.Column;
import jakarta.persistence.MappedSuperclass;
import jakarta.validation.constraints.NotEmpty;

/**
 * Simple JavaBean domain object representing an person.
 *
 * @author Ken Krebs
 */
@MappedSuperclass
public class Person extends BaseEntity {

	@Column(name = "first_name")
	@NotEmpty
	private String firstName;

	@Column(name = "last_name")
	@NotEmpty
	private String lastName;

	public String getFirstName() {
		return this.firstName;
	}

	public void setFirstName(String firstName) {
		this.firstName = firstName;
	}

	public String getLastName() {
		return this.lastName;
	}

	public void setLastName(String lastName) {
		this.lastName = lastName;
	}

}
```
