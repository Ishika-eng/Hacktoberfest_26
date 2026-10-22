# Migration report

- App: `spring-petclinic-rest`  |  Model: `qwen2.5-coder:7b-instruct`  |  Upgrade tool: OpenRewrite (rewrite-spring 6.37.1)
- Spring Boot parent after upgrade: `3.3.13`
- Result: **NEEDS HUMAN REVIEW (tests failing)**
- Model fix rounds: 0 (max 5)
- Settings: temperature 0, seed 0, 8192-token context; output fingerprint `0542475cf487` (identical fingerprints across runs mean identical generated code)

## Build score per run

Score = failing tests, or 1000+ compile errors. 0 means green. A run that scores worse than the best so far is rolled back.

| Run | Score | Tests passed | What happened |
|---|---|---|---|
| 1 | 1100 | - | build |

## Test integrity

- Existing files under `src/test` (tests and test resources) and every `pom.xml` / `.mvn` file are hashed after the upgrade tool runs and again at the end. The fix loop can only write under `src/main`.
- The upgraded pom must not gain test-skipping settings (`skipTests`, `maven.test.skip`, `testFailureIgnore`, surefire `skip` or excludes).
- A passing run must execute exactly the baseline's tests: the original app ran 172 tests, 172 passed.
- Result: no violations.

The upgrade tool itself (not the model) rewrote these test files: `src/test/java/org/springframework/samples/petclinic/model/ValidatorTests.java`, `src/test/resources/application.properties`

## Diff (all changes to Java sources, including the upgrade tool's)
```diff
--- a/BaseEntity.java
+++ b/BaseEntity.java
@@ -15,10 +15,10 @@
  */
 package org.springframework.samples.petclinic.model;
 
-import javax.persistence.GeneratedValue;
-import javax.persistence.GenerationType;
-import javax.persistence.Id;
-import javax.persistence.MappedSuperclass;
+import jakarta.persistence.GeneratedValue;
+import jakarta.persistence.GenerationType;
+import jakarta.persistence.Id;
+import jakarta.persistence.MappedSuperclass;
 
 import com.fasterxml.jackson.annotation.JsonIgnore;
 

--- a/NamedEntity.java
+++ b/NamedEntity.java
@@ -15,10 +15,10 @@
  */
 package org.springframework.samples.petclinic.model;
 
-import javax.persistence.Column;
-import javax.persistence.MappedSuperclass;
+import jakarta.persistence.Column;
+import jakarta.persistence.MappedSuperclass;
 
-import javax.validation.constraints.NotEmpty;
+import jakarta.validation.constraints.NotEmpty;
 
 
 /**

--- a/Owner.java
+++ b/Owner.java
@@ -19,9 +19,14 @@
 import org.springframework.beans.support.PropertyComparator;
 import org.springframework.core.style.ToStringCreator;
 
-import javax.persistence.*;
-import javax.validation.constraints.Digits;
-import javax.validation.constraints.NotEmpty;
+import jakarta.persistence.CascadeType;
+import jakarta.persistence.Column;
+import jakarta.persistence.Entity;
+import jakarta.persistence.FetchType;
+import jakarta.persistence.OneToMany;
+import jakarta.persistence.Table;
+import jakarta.validation.constraints.Digits;
+import jakarta.validation.constraints.NotEmpty;
 import java.util.*;
 
 

--- a/Person.java
+++ b/Person.java
@@ -15,10 +15,10 @@
  */
 package org.springframework.samples.petclinic.model;
 
-import javax.persistence.Column;
-import javax.persistence.MappedSuperclass;
+import jakarta.persistence.Column;
+import jakarta.persistence.MappedSuperclass;
 
-import javax.validation.constraints.NotEmpty;
+import jakarta.validation.constraints.NotEmpty;
 
 /**
  * Simple JavaBean domain object representing an person.

--- a/Pet.java
+++ b/Pet.java
@@ -19,7 +19,14 @@
 import org.springframework.beans.support.PropertyComparator;
 import org.springframework.format.annotation.DateTimeFormat;
 
-import javax.persistence.*;
+import jakarta.persistence.CascadeType;
+import jakarta.persistence.Column;
+import jakarta.persistence.Entity;
+import jakarta.persistence.FetchType;
+import jakarta.persistence.JoinColumn;
+import jakarta.persistence.ManyToOne;
+import jakarta.persistence.OneToMany;
+import jakarta.persistence.Table;
 import java.time.LocalDate;
 import java.util.*;
 

--- a/PetType.java
+++ b/PetType.java
@@ -15,8 +15,8 @@
  */
 package org.springframework.samples.petclinic.model;
 
-import javax.persistence.Entity;
-import javax.persistence.Table;
+import jakarta.persistence.Entity;
+import jakarta.persistence.Table;
 
 /**
  * @author Juergen Hoeller

--- a/Role.java
+++ b/Role.java
@@ -1,11 +1,11 @@
 package org.springframework.samples.petclinic.model;
 
-import javax.persistence.Column;
-import javax.persistence.Entity;
-import javax.persistence.JoinColumn;
-import javax.persistence.ManyToOne;
-import javax.persistence.Table;
-import javax.persistence.UniqueConstraint;
+import jakarta.persistence.Column;
+import jakarta.persistence.Entity;
+import jakarta.persistence.JoinColumn;
+import jakarta.persistence.ManyToOne;
+import jakarta.persistence.Table;
+import jakarta.persistence.UniqueConstraint;
 
 import com.fasterxml.jackson.annotation.JsonIgnore;
 

--- a/Specialty.java
+++ b/Specialty.java
@@ -15,8 +15,8 @@
  */
 package org.springframework.samples.petclinic.model;
 
-import javax.persistence.Entity;
-import javax.persistence.Table;
+import jakarta.persistence.Entity;
+import jakarta.persistence.Table;
 
 /**
  * Models a {@link Vet Vet's} specialty (for example, dentistry).

--- a/User.java
+++ b/User.java
@@ -3,13 +3,13 @@
 import java.util.HashSet;
 import java.util.Set;
 
-import javax.persistence.CascadeType;
-import javax.persistence.Column;
-import javax.persistence.Entity;
-import javax.persistence.FetchType;
-import javax.persistence.Id;
-import javax.persistence.OneToMany;
-import javax.persistence.Table;
+import jakarta.persistence.CascadeType;
+import jakarta.persistence.Column;
+import jakarta.persistence.Entity;
+import jakarta.persistence.FetchType;
+import jakarta.persistence.Id;
+import jakarta.persistence.OneToMany;
+import jakarta.persistence.Table;
 
 import com.fasterxml.jackson.annotation.JsonIgnore;
 

--- a/Vet.java
+++ b/Vet.java
@@ -19,8 +19,13 @@
 import org.springframework.beans.support.MutableSortDefinition;
 import org.springframework.beans.support.PropertyComparator;
 
-import javax.persistence.*;
-import javax.xml.bind.annotation.XmlElement;
+import jakarta.persistence.Entity;
+import jakarta.persistence.FetchType;
+import jakarta.persistence.JoinColumn;
+import jakarta.persistence.JoinTable;
+import jakarta.persistence.ManyToMany;
+import jakarta.persistence.Table;
+import jakarta.xml.bind.annotation.XmlElement;
 import java.util.*;
 
 /**

--- a/Visit.java
+++ b/Visit.java
@@ -17,8 +17,8 @@
 
 import org.springframework.format.annotation.DateTimeFormat;
 
-import javax.persistence.*;
-import javax.validation.constraints.NotEmpty;
+import jakarta.persistence.*;
+import jakarta.validation.constraints.NotEmpty;
 import java.time.LocalDate;
 
 /**

--- a/JdbcOwnerRepositoryImpl.java
+++ b/JdbcOwnerRepositoryImpl.java
@@ -15,7 +15,7 @@
  */
 package org.springframework.samples.petclinic.repository.jdbc;
 
-import org.springframework.beans.factory.annotation.Autowired;
+import org.springframework.boot.sql.init.dependency.DependsOnDatabaseInitialization;
 import org.springframework.context.annotation.Profile;
 import org.springframework.dao.DataAccessException;
 import org.springframework.dao.EmptyResultDataAccessException;
@@ -33,7 +33,7 @@
 import org.springframework.stereotype.Repository;
 
 import javax.sql.DataSource;
-import javax.transaction.Transactional;
+import jakarta.transaction.Transactional;
 import java.util.Collection;
 import java.util.HashMap;
 import java.util.List;
@@ -51,6 +51,7 @@
  * @author Antoine Rey
  * @author Vitaliy Fedoriv
  */
+@DependsOnDatabaseInitialization
 @Repository
 @Profile("jdbc")
 public class JdbcOwnerRepositoryImpl implements OwnerRepository {
@@ -59,7 +60,6 @@
 
     private SimpleJdbcInsert insertOwner;
 
-    @Autowired
     public JdbcOwnerRepositoryImpl(DataSource dataSource) {
 
         this.insertOwner = new SimpleJdbcInsert(dataSource)

--- a/JdbcPetRepositoryImpl.java
+++ b/JdbcPetRepositoryImpl.java
@@ -23,7 +23,7 @@
 
 import javax.sql.DataSource;
 
-import org.springframework.beans.factory.annotation.Autowired;
+import org.springframework.boot.sql.init.dependency.DependsOnDatabaseInitialization;
 import org.springframework.context.annotation.Profile;
 import org.springframework.dao.DataAccessException;
 import org.springframework.dao.EmptyResultDataAccessException;
@@ -51,6 +51,7 @@
  * @author Mark Fisher
  * @author Vitaliy Fedoriv
  */
+@DependsOnDatabaseInitialization
 @Repository
 @Profile("jdbc")
 public class JdbcPetRepositoryImpl implements PetRepository {
@@ -64,7 +65,6 @@
     private VisitRepository visitRepository;
 
 
-    @Autowired
     public JdbcPetRepositoryImpl(DataSource dataSource,
     		OwnerRepository ownerRepository,
     		VisitRepository visitRepository) {

--- a/JdbcPetTypeRepositoryImpl.java
+++ b/JdbcPetTypeRepositoryImpl.java
@@ -24,7 +24,7 @@
 
 import javax.sql.DataSource;
 
-import org.springframework.beans.factory.annotation.Autowired;
+import org.springframework.boot.sql.init.dependency.DependsOnDatabaseInitialization;
 import org.springframework.context.annotation.Profile;
 import org.springframework.dao.DataAccessException;
 import org.springframework.dao.EmptyResultDataAccessException;
@@ -44,6 +44,7 @@
  *
  */
 
+@DependsOnDatabaseInitialization
 @Repository
 @Profile("jdbc")
 public class JdbcPetTypeRepositoryImpl implements PetTypeRepository {
@@ -52,7 +53,6 @@
 	
 	private SimpleJdbcInsert insertPetType;
 	
-	@Autowired
 	public JdbcPetTypeRepositoryImpl(DataSource dataSource) {
 		this.namedParameterJdbcTemplate = new NamedParameterJdbcTemplate(dataSource);
 		this.insertPetType = new SimpleJdbcInsert(dataSource)

--- a/JdbcSpecialtyRepositoryImpl.java
+++ b/JdbcSpecialtyRepositoryImpl.java
@@ -22,7 +22,7 @@
 
 import javax.sql.DataSource;
 
-import org.springframework.beans.factory.annotation.Autowired;
+import org.springframework.boot.sql.init.dependency.DependsOnDatabaseInitialization;
 import org.springframework.context.annotation.Profile;
 import org.springframework.dao.DataAccessException;
 import org.springframework.dao.EmptyResultDataAccessException;
@@ -40,6 +40,7 @@
  *
  */
 
+@DependsOnDatabaseInitialization
 @Repository
 @Profile("jdbc")
 public class JdbcSpecialtyRepositoryImpl implements SpecialtyRepository {
@@ -48,7 +49,6 @@
 	
 	private SimpleJdbcInsert insertSpecialty;
 
-	@Autowired
 	public JdbcSpecialtyRepositoryImpl(DataSource dataSource) {
 		this.namedParameterJdbcTemplate = new NamedParameterJdbcTemplate(dataSource);
 		this.insertSpecialty = new SimpleJdbcInsert(dataSource)

--- a/JdbcUserRepositoryImpl.java
+++ b/JdbcUserRepositoryImpl.java
@@ -5,7 +5,7 @@
 
 import javax.sql.DataSource;
 
-import org.springframework.beans.factory.annotation.Autowired;
+import org.springframework.boot.sql.init.dependency.DependsOnDatabaseInitialization;
 import org.springframework.context.annotation.Profile;
 import org.springframework.dao.DataAccessException;
 import org.springframework.dao.EmptyResultDataAccessException;
@@ -18,6 +18,7 @@
 import org.springframework.samples.petclinic.repository.UserRepository;
 import org.springframework.stereotype.Repository;
 
+@DependsOnDatabaseInitialization
 @Repository
 @Profile("jdbc")
 public class JdbcUserRepositoryImpl implements UserRepository {
@@ -25,7 +26,6 @@
     private NamedParameterJdbcTemplate namedParameterJdbcTemplate;
     private SimpleJdbcInsert insertUser;
 
-    @Autowired
     public JdbcUserRepositoryImpl(DataSource dataSource) {
         this.namedParameterJdbcTemplate = new NamedParameterJdbcTemplate(dataSource);
         this.insertUser = new SimpleJdbcInsert(dataSource).withTableName("users");

--- a/JdbcVetRepositoryImpl.java
+++ b/JdbcVetRepositoryImpl.java
@@ -25,7 +25,7 @@
 
 import javax.sql.DataSource;
 
-import org.springframework.beans.factory.annotation.Autowired;
+import org.springframework.boot.sql.init.dependency.DependsOnDatabaseInitialization;
 import org.springframework.context.annotation.Profile;
 import org.springframework.dao.DataAccessException;
 import org.springframework.dao.EmptyResultDataAccessException;
@@ -53,6 +53,7 @@
  * @author Michael Isvy
  * @author Vitaliy Fedoriv
  */
+@DependsOnDatabaseInitialization
 @Repository
 @Profile("jdbc")
 public class JdbcVetRepositoryImpl implements VetRepository {
@@ -61,7 +62,6 @@
 	private NamedParameterJdbcTemplate namedParameterJdbcTemplate;
 	private SimpleJdbcInsert insertVet;
 
-    @Autowired
     public JdbcVetRepositoryImpl(DataSource dataSource, JdbcTemplate jdbcTemplate) {
         this.jdbcTemplate = jdbcTemplate;
 		this.insertVet = new SimpleJdbcInsert(dataSource).withTableName("vets").usingGeneratedKeyColumns("id");

--- a/JdbcVisitRepositoryImpl.java
+++ b/JdbcVisitRepositoryImpl.java
@@ -15,7 +15,7 @@
  */
 package org.springframework.samples.petclinic.repository.jdbc;
 
-import org.springframework.beans.factory.annotation.Autowired;
+import org.springframework.boot.sql.init.dependency.DependsOnDatabaseInitialization;
 import org.springframework.context.annotation.Profile;
 import org.springframework.dao.DataAccessException;
 import org.springframework.dao.EmptyResultDataAccessException;
@@ -48,6 +48,7 @@
  * @author Michael Isvy
  * @author Vitaliy Fedoriv
  */
+@DependsOnDatabaseInitialization
 @Repository
 @Profile("jdbc")
 public class JdbcVisitRepositoryImpl implements VisitRepository {
@@ -55,7 +56,6 @@
     protected SimpleJdbcInsert insertVisit;
     private NamedParameterJdbcTemplate namedParameterJdbcTemplate;
 
-    @Autowired
     public JdbcVisitRepositoryImpl(DataSource dataSource) {
         this.namedParameterJdbcTemplate = new NamedParameterJdbcTemplate(dataSource);
 

--- a/JpaOwnerRepositoryImpl.java
+++ b/JpaOwnerRepositoryImpl.java
@@ -17,9 +17,9 @@
 
 import java.util.Collection;
 
-import javax.persistence.EntityManager;
-import javax.persistence.PersistenceContext;
-import javax.persistence.Query;
+import jakarta.persistence.EntityManager;
+import jakarta.persistence.PersistenceContext;
+import jakarta.persistence.Query;
 
 import org.springframework.context.annotation.Profile;
 import org.springframework.dao.DataAccessException;

--- a/JpaPetRepositoryImpl.java
+++ b/JpaPetRepositoryImpl.java
@@ -18,8 +18,8 @@
 import java.util.Collection;
 import java.util.List;
 
-import javax.persistence.EntityManager;
-import javax.persistence.PersistenceContext;
+import jakarta.persistence.EntityManager;
+import jakarta.persistence.PersistenceContext;
 
 import org.springframework.context.annotation.Profile;
 import org.springframework.dao.DataAccessException;

--- a/JpaPetTypeRepositoryImpl.java
+++ b/JpaPetTypeRepositoryImpl.java
@@ -20,8 +20,8 @@
 import java.util.Collection;
 import java.util.List;
 
-import javax.persistence.EntityManager;
-import javax.persistence.PersistenceContext;
+import jakarta.persistence.EntityManager;
+import jakarta.persistence.PersistenceContext;
 
 import org.springframework.context.annotation.Profile;
 import org.springframework.dao.DataAccessException;

--- a/JpaSpecialtyRepositoryImpl.java
+++ b/JpaSpecialtyRepositoryImpl.java
@@ -18,8 +18,8 @@
 
 import java.util.Collection;
 
-import javax.persistence.EntityManager;
-import javax.persistence.PersistenceContext;
+import jakarta.persistence.EntityManager;
+import jakarta.persistence.PersistenceContext;
 
 import org.springframework.context.annotation.Profile;
 import org.springframework.dao.DataAccessException;

--- a/JpaUserRepositoryImpl.java
+++ b/JpaUserRepositoryImpl.java
@@ -1,7 +1,7 @@
 package org.springframework.samples.petclinic.repository.jpa;
 
-import javax.persistence.EntityManager;
-import javax.persistence.PersistenceContext;
+import jakarta.persistence.EntityManager;
+import jakarta.persistence.PersistenceContext;
 
 import org.springframework.context.annotation.Profile;
 import org.springframework.dao.DataAccessException;

--- a/JpaVetRepositoryImpl.java
+++ b/JpaVetRepositoryImpl.java
@@ -21,8 +21,8 @@
 import org.springframework.samples.petclinic.repository.VetRepository;
 import org.springframework.stereotype.Repository;
 
-import javax.persistence.EntityManager;
-import javax.persistence.PersistenceContext;
+import jakarta.persistence.EntityManager;
+import jakarta.persistence.PersistenceContext;
 import java.util.Collection;
 
 /**

--- a/JpaVisitRepositoryImpl.java
+++ b/JpaVisitRepositoryImpl.java
@@ -18,9 +18,9 @@
 import java.util.Collection;
 import java.util.List;
 
-import javax.persistence.EntityManager;
-import javax.persistence.PersistenceContext;
-import javax.persistence.Query;
+import jakarta.persistence.EntityManager;
+import jakarta.persistence.PersistenceContext;
+import jakarta.persistence.Query;
 
 import org.springframework.context.annotation.Profile;
 import org.springframework.dao.DataAccessException;

--- a/SpringDataPetRepositoryImpl.java
+++ b/SpringDataPetRepositoryImpl.java
@@ -16,8 +16,8 @@
 
 package org.springframework.samples.petclinic.repository.springdatajpa;
 
-import javax.persistence.EntityManager;
-import javax.persistence.PersistenceContext;
+import jakarta.persistence.EntityManager;
+import jakarta.persistence.PersistenceContext;
 
 import org.springframework.context.annotation.Profile;
 import org.springframework.samples.petclinic.model.Pet;

--- a/SpringDataPetTypeRepositoryImpl.java
+++ b/SpringDataPetTypeRepositoryImpl.java
@@ -21,8 +21,8 @@
 import org.springframework.samples.petclinic.model.PetType;
 import org.springframework.samples.petclinic.model.Visit;
 
-import javax.persistence.EntityManager;
-import javax.persistence.PersistenceContext;
+import jakarta.persistence.EntityManager;
+import jakarta.persistence.PersistenceContext;
 import java.util.List;
 
 /**

--- a/SpringDataSpecialtyRepositoryImpl.java
+++ b/SpringDataSpecialtyRepositoryImpl.java
@@ -16,8 +16,8 @@
 
 package org.springframework.samples.petclinic.repository.springdatajpa;
 
-import javax.persistence.EntityManager;
-import javax.persistence.PersistenceContext;
+import jakarta.persistence.EntityManager;
+import jakarta.persistence.PersistenceContext;
 
 import org.springframework.context.annotation.Profile;
 import org.springframework.samples.petclinic.model.Specialty;

--- a/SpringDataVisitRepositoryImpl.java
+++ b/SpringDataVisitRepositoryImpl.java
@@ -16,8 +16,8 @@
 
 package org.springframework.samples.petclinic.repository.springdatajpa;
 
-import javax.persistence.EntityManager;
-import javax.persistence.PersistenceContext;
+import jakarta.persistence.EntityManager;
+import jakarta.persistence.PersistenceContext;
 
 import org.springframework.context.annotation.Profile;
 import org.springframework.dao.DataAccessException;

--- a/OwnerRestController.java
+++ b/OwnerRestController.java
@@ -19,7 +19,7 @@
 import java.util.Collection;
 import java.util.List;
 
-import javax.transaction.Transactional;
+import jakarta.transaction.Transactional;
 
 import org.springframework.http.HttpHeaders;
 import org.springframework.http.HttpStatus;

--- a/PetRestController.java
+++ b/PetRestController.java
@@ -19,7 +19,7 @@
 import java.util.ArrayList;
 import java.util.List;
 
-import javax.transaction.Transactional;
+import jakarta.transaction.Transactional;
 
 import org.springframework.http.HttpStatus;
 import org.springframework.http.ResponseEntity;

--- a/PetTypeRestController.java
+++ b/PetTypeRestController.java
@@ -19,7 +19,7 @@
 import java.util.ArrayList;
 import java.util.List;
 
-import javax.transaction.Transactional;
+import jakarta.transaction.Transactional;
 
 import org.springframework.http.HttpHeaders;
 import org.springframework.http.HttpStatus;

--- a/RootRestController.java
+++ b/RootRestController.java
@@ -18,7 +18,7 @@
 
 import java.io.IOException;
 
-import javax.servlet.http.HttpServletResponse;
+import jakarta.servlet.http.HttpServletResponse;
 
 import org.springframework.beans.factory.annotation.Value;
 import org.springframework.web.bind.annotation.CrossOrigin;

--- a/SpecialtyRestController.java
+++ b/SpecialtyRestController.java
@@ -19,7 +19,7 @@
 import java.util.ArrayList;
 import java.util.List;
 
-import javax.transaction.Transactional;
+import jakarta.transaction.Transactional;
 
 import org.springframework.http.HttpHeaders;
 import org.springframework.http.HttpStatus;

--- a/UserRestController.java
+++ b/UserRestController.java
@@ -30,7 +30,7 @@
 import org.springframework.web.bind.annotation.RequestMapping;
 import org.springframework.web.bind.annotation.RestController;
 
-import javax.validation.Valid;
+import jakarta.validation.Valid;
 
 @RestController
 @CrossOrigin(exposedHeaders = "errors, content-type")

--- a/VetRestController.java
+++ b/VetRestController.java
@@ -18,7 +18,7 @@
 import java.util.ArrayList;
 import java.util.List;
 
-import javax.transaction.Transactional;
+import jakarta.transaction.Transactional;
 
 import org.springframework.http.HttpHeaders;
 import org.springframework.http.HttpStatus;

--- a/VisitRestController.java
+++ b/VisitRestController.java
@@ -19,7 +19,7 @@
 import java.util.ArrayList;
 import java.util.List;
 
-import javax.transaction.Transactional;
+import jakarta.transaction.Transactional;
 
 import org.springframework.http.HttpHeaders;
 import org.springframework.http.HttpStatus;

--- a/BasicAuthenticationConfig.java
+++ b/BasicAuthenticationConfig.java
@@ -3,37 +3,38 @@
 import javax.sql.DataSource;
 
 import org.springframework.beans.factory.annotation.Autowired;
+
+import static org.springframework.security.config.Customizer.withDefaults;
 import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
 import org.springframework.context.annotation.Bean;
 import org.springframework.context.annotation.Configuration;
 import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
-import org.springframework.security.config.annotation.method.configuration.EnableGlobalMethodSecurity;
+import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
 import org.springframework.security.config.annotation.web.builders.HttpSecurity;
 import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
-import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
 import org.springframework.security.crypto.factory.PasswordEncoderFactories;
 import org.springframework.security.crypto.password.PasswordEncoder;
+import org.springframework.security.web.SecurityFilterChain;
 
 @Configuration
-@EnableGlobalMethodSecurity(prePostEnabled = true) // Enable @PreAuthorize method-level security
+@EnableMethodSecurity // Enable @PreAuthorize method-level security
 @ConditionalOnProperty(name = "petclinic.security.enable", havingValue = "true")
-public class BasicAuthenticationConfig extends WebSecurityConfigurerAdapter {
+public class BasicAuthenticationConfig {
 
     @Autowired
     private DataSource dataSource;
 
-    @Override
-    protected void configure(HttpSecurity http) throws Exception {
+    @Bean
+    SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
         // @formatter:off
         http
-            .authorizeRequests()
+            .authorizeHttpRequests(requests -> requests
                 .anyRequest()
-                    .authenticated()
-                    .and()
-                .httpBasic()
-                    .and()
-                .csrf()
-                    .disable();
+                .authenticated())
+            .httpBasic(withDefaults())
+            .csrf(csrf -> csrf
+                .disable());
+        return http.build();
         // @formatter:on
     }
 

--- a/DisableSecurityConfig.java
+++ b/DisableSecurityConfig.java
@@ -1,9 +1,10 @@
 package org.springframework.samples.petclinic.security;
 
 import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
+import org.springframework.context.annotation.Bean;
 import org.springframework.context.annotation.Configuration;
 import org.springframework.security.config.annotation.web.builders.HttpSecurity;
-import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
+import org.springframework.security.web.SecurityFilterChain;
 
 /**
  * Starting from Spring Boot 2, if Spring Security is present, endpoints are secured by default
@@ -11,17 +12,17 @@
  */
 @Configuration
 @ConditionalOnProperty(name = "petclinic.security.enable", havingValue = "false")
-public class DisableSecurityConfig extends WebSecurityConfigurerAdapter {
+public class DisableSecurityConfig {
 
-    @Override
-    protected void configure(HttpSecurity http) throws Exception {
+    @Bean
+    SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
         // @formatter:off
         http
-            .authorizeRequests()
-                .anyRequest().permitAll()
-                .and()
-            .csrf()
-                .disable();
+            .authorizeHttpRequests(requests -> requests
+                .anyRequest().permitAll())
+            .csrf(csrf -> csrf
+                .disable());
+        return http.build();
         // @formatter:on
     }
 }

--- a/ClinicServiceImpl.java
+++ b/ClinicServiceImpl.java
@@ -17,7 +17,6 @@
 
 import java.util.Collection;
 
-import org.springframework.beans.factory.annotation.Autowired;
 import org.springframework.cache.annotation.Cacheable;
 import org.springframework.dao.DataAccessException;
 import org.springframework.dao.EmptyResultDataAccessException;
@@ -54,8 +53,7 @@
     private SpecialtyRepository specialtyRepository;
 	private PetTypeRepository petTypeRepository;
 
-    @Autowired
-     public ClinicServiceImpl(
+    public ClinicServiceImpl(
        		 PetRepository petRepository,
     		 VetRepository vetRepository,
     		 OwnerRepository ownerRepository,

--- a/ValidatorTests.java
+++ b/ValidatorTests.java
@@ -5,8 +5,8 @@
 import java.util.Locale;
 import java.util.Set;
 
-import javax.validation.ConstraintViolation;
-import javax.validation.Validator;
+import jakarta.validation.ConstraintViolation;
+import jakarta.validation.Validator;
 
 import org.junit.jupiter.api.Test;
 import org.springframework.context.i18n.LocaleContextHolder;

--- a/OwnerMapperImpl.java
+++ b/OwnerMapperImpl.java
@@ -0,0 +1,132 @@
+package org.springframework.samples.petclinic.mapper;
+
+import java.util.ArrayList;
+import java.util.Collection;
+import java.util.List;
+import javax.annotation.processing.Generated;
+import org.springframework.beans.factory.annotation.Autowired;
+import org.springframework.samples.petclinic.model.Owner;
+import org.springframework.samples.petclinic.model.Pet;
+import org.springframework.samples.petclinic.rest.dto.OwnerDto;
+import org.springframework.samples.petclinic.rest.dto.OwnerFieldsDto;
+import org.springframework.samples.petclinic.rest.dto.PetDto;
+import org.springframework.stereotype.Component;
+
+@Generated(
+    value = "org.mapstruct.ap.MappingProcessor"
+)
+@Component
+public class OwnerMapperImpl implements OwnerMapper {
+
+    @Autowired
+    private PetMapper petMapper;
+
+    @Override
+    public OwnerDto toOwnerDto(Owner owner) {
+        if ( owner == null ) {
+            return null;
+        }
+
+        OwnerDto ownerDto = new OwnerDto();
+
+        ownerDto.setFirstName( owner.getFirstName() );
+        ownerDto.setLastName( owner.getLastName() );
+        ownerDto.setAddress( owner.getAddress() );
+        ownerDto.setCity( owner.getCity() );
+        ownerDto.setTelephone( owner.getTelephone() );
+        ownerDto.setId( owner.getId() );
+        ownerDto.setPets( petListToPetDtoList( owner.getPets() ) );
+
+        return ownerDto;
+    }
+
+    @Override
+    public Owner toOwner(OwnerDto ownerDto) {
+        if ( ownerDto == null ) {
+            return null;
+        }
+
+        Owner owner = new Owner();
+
+        owner.setId( ownerDto.getId() );
+        owner.setFirstName( ownerDto.getFirstName() );
+        owner.setLastName( ownerDto.getLastName() );
+        owner.setAddress( ownerDto.getAddress() );
+        owner.setCity( ownerDto.getCity() );
+        owner.setTelephone( ownerDto.getTelephone() );
+        owner.setPets( petDtoListToPetList( ownerDto.getPets() ) );
+
+        return owner;
+    }
+
+    @Override
+    public Owner toOwner(OwnerFieldsDto ownerDto) {
+        if ( ownerDto == null ) {
+            return null;
+        }
+
+        Owner owner = new Owner();
+
+        owner.setFirstName( ownerDto.getFirstName() );
+        owner.setLastName( ownerDto.getLastName() );
+        owner.setAddress( ownerDto.getAddress() );
+        owner.setCity( ownerDto.getCity() );
+        owner.setTelephone( ownerDto.getTelephone() );
+
+        return owner;
+    }
+
+    @Override
+    public List<OwnerDto> toOwnerDtoCollection(Collection<Owner> ownerCollection) {
+        if ( ownerCollection == null ) {
+            return null;
+        }
+
+        List<OwnerDto> list = new ArrayList<OwnerDto>( ownerCollection.size() );
+        for ( Owner owner : ownerCollection ) {
+            list.add( toOwnerDto( owner ) );
+        }
+
+        return list;
+    }
+
+    @Override
+    public Collection<Owner> toOwners(Collection<OwnerDto> ownerDtos) {
+        if ( ownerDtos == null ) {
+            return null;
+        }
+
+        Collection<Owner> collection = new ArrayList<Owner>( ownerDtos.size() );
+        for ( OwnerDto ownerDto : ownerDtos ) {
+            collection.add( toOwner( ownerDto ) );
+        }
+
+        return collection;
+    }
+
+    protected List<PetDto> petListToPetDtoList(List<Pet> list) {
+        if ( list == null ) {
+            return null;
+        }
+
+        List<PetDto> list1 = new ArrayList<PetDto>( list.size() );
+        for ( Pet pet : list ) {
+            list1.add( petMapper.toPetDto( pet ) );
+        }
+
+        return list1;
+    }
+
+    protected List<Pet> petDtoListToPetList(List<PetDto> list) {
+        if ( list == null ) {
+            return null;
+        }
+
+        List<Pet> list1 = new ArrayList<Pet>( list.size() );
+        for ( PetDto petDto : list ) {
+            list1.add( petMapper.toPet( petDto ) );
+        }
+
+        return list1;
+    }
+}

--- a/PetMapperImpl.java
+++ b/PetMapperImpl.java
@@ -0,0 +1,204 @@
+package org.springframework.samples.petclinic.mapper;
+
+import java.util.ArrayList;
+import java.util.Collection;
+import java.util.List;
+import javax.annotation.processing.Generated;
+import org.springframework.samples.petclinic.model.Owner;
+import org.springframework.samples.petclinic.model.Pet;
+import org.springframework.samples.petclinic.model.PetType;
+import org.springframework.samples.petclinic.model.Visit;
+import org.springframework.samples.petclinic.rest.dto.PetDto;
+import org.springframework.samples.petclinic.rest.dto.PetFieldsDto;
+import org.springframework.samples.petclinic.rest.dto.PetTypeDto;
+import org.springframework.samples.petclinic.rest.dto.VisitDto;
+import org.springframework.stereotype.Component;
+
+@Generated(
+    value = "org.mapstruct.ap.MappingProcessor"
+)
+@Component
+public class PetMapperImpl implements PetMapper {
+
+    @Override
+    public PetDto toPetDto(Pet pet) {
+        if ( pet == null ) {
+            return null;
+        }
+
+        PetDto petDto = new PetDto();
+
+        petDto.setOwnerId( petOwnerId( pet ) );
+        petDto.setName( pet.getName() );
+        petDto.setBirthDate( pet.getBirthDate() );
+        petDto.setType( toPetTypeDto( pet.getType() ) );
+        petDto.setId( pet.getId() );
+        petDto.setVisits( visitListToVisitDtoList( pet.getVisits() ) );
+
+        return petDto;
+    }
+
+    @Override
+    public Collection<PetDto> toPetsDto(Collection<Pet> pets) {
+        if ( pets == null ) {
+            return null;
+        }
+
+        Collection<PetDto> collection = new ArrayList<PetDto>( pets.size() );
+        for ( Pet pet : pets ) {
+            collection.add( toPetDto( pet ) );
+        }
+
+        return collection;
+    }
+
+    @Override
+    public Collection<Pet> toPets(Collection<PetDto> pets) {
+        if ( pets == null ) {
+            return null;
+        }
+
+        Collection<Pet> collection = new ArrayList<Pet>( pets.size() );
+        for ( PetDto petDto : pets ) {
+            collection.add( toPet( petDto ) );
+        }
+
+        return collection;
+    }
+
+    @Override
+    public Pet toPet(PetDto petDto) {
+        if ( petDto == null ) {
+            return null;
+        }
+
+        Pet pet = new Pet();
+
+        pet.setId( petDto.getId() );
+        pet.setName( petDto.getName() );
+        pet.setBirthDate( petDto.getBirthDate() );
+        pet.setType( toPetType( petDto.getType() ) );
+        pet.setVisits( visitDtoListToVisitList( petDto.getVisits() ) );
+
+        return pet;
+    }
+
+    @Override
+    public Pet toPet(PetFieldsDto petFieldsDto) {
+        if ( petFieldsDto == null ) {
+            return null;
+        }
+
+        Pet pet = new Pet();
+
+        pet.setName( petFieldsDto.getName() );
+        pet.setBirthDate( petFieldsDto.getBirthDate() );
+        pet.setType( toPetType( petFieldsDto.getType() ) );
+
+        return pet;
+    }
+
+    @Override
+    public PetTypeDto toPetTypeDto(PetType petType) {
+        if ( petType == null ) {
+            return null;
+        }
+
+        PetTypeDto petTypeDto = new PetTypeDto();
+
+        petTypeDto.setName( petType.getName() );
+        petTypeDto.setId( petType.getId() );
+
+        return petTypeDto;
+    }
+
+    @Override
+    public PetType toPetType(PetTypeDto petTypeDto) {
+        if ( petTypeDto == null ) {
+            return null;
+        }
+
+        PetType petType = new PetType();
+
+        petType.setId( petTypeDto.getId() );
+        petType.setName( petTypeDto.getName() );
+
+        return petType;
+    }
+
+    @Override
+    public Collection<PetTypeDto> toPetTypeDtos(Collection<PetType> petTypes) {
+        if ( petTypes == null ) {
+            return null;
+        }
+
+        Collection<PetTypeDto> collection = new ArrayList<PetTypeDto>( petTypes.size() );
+        for ( PetType petType : petTypes ) {
+            collection.add( toPetTypeDto( petType ) );
+        }
+
+        return collection;
+    }
+
+    private Integer petOwnerId(Pet pet) {
+        Owner owner = pet.getOwner();
+        if ( owner == null ) {
+            return null;
+        }
+        return owner.getId();
+    }
+
+    protected VisitDto visitToVisitDto(Visit visit) {
+        if ( visit == null ) {
+            return null;
+        }
+
+        VisitDto visitDto = new VisitDto();
+
+        visitDto.setDate( visit.getDate() );
+        visitDto.setDescription( visit.getDescription() );
+        visitDto.setId( visit.getId() );
+
+        return visitDto;
+    }
+
+    protected List<VisitDto> visitListToVisitDtoList(List<Visit> list) {
+        if ( list == null ) {
+            return null;
+        }
+
+        List<VisitDto> list1 = new ArrayList<VisitDto>( list.size() );
+        for ( Visit visit : list ) {
+            list1.add( visitToVisitDto( visit ) );
+        }
+
+        return list1;
+    }
+
+    protected Visit visitDtoToVisit(VisitDto visitDto) {
+        if ( visitDto == null ) {
+            return null;
+        }
+
+        Visit visit = new Visit();
+
+        visit.setId( visitDto.getId() );
+        visit.setDate( visitDto.getDate() );
+        visit.setDescription( visitDto.getDescription() );
+
+        return visit;
+    }
+
+    protected List<Visit> visitDtoListToVisitList(List<VisitDto> list) {
+        if ( list == null ) {
+            return null;
+        }
+
+        List<Visit> list1 = new ArrayList<Visit>( list.size() );
+        for ( VisitDto visitDto : list ) {
+            list1.add( visitDtoToVisit( visitDto ) );
+        }
+
+        return list1;
+    }
+}

--- a/PetTypeMapperImpl.java
+++ b/PetTypeMapperImpl.java
@@ -0,0 +1,72 @@
+package org.springframework.samples.petclinic.mapper;
+
+import java.util.ArrayList;
+import java.util.Collection;
+import java.util.List;
+import javax.annotation.processing.Generated;
+import org.springframework.samples.petclinic.model.PetType;
+import org.springframework.samples.petclinic.rest.dto.PetTypeDto;
+import org.springframework.samples.petclinic.rest.dto.PetTypeFieldsDto;
+import org.springframework.stereotype.Component;
+
+@Generated(
+    value = "org.mapstruct.ap.MappingProcessor"
+)
+@Component
+public class PetTypeMapperImpl implements PetTypeMapper {
+
+    @Override
+    public PetType toPetType(PetTypeDto petTypeDto) {
+        if ( petTypeDto == null ) {
+            return null;
+        }
+
+        PetType petType = new PetType();
+
+        petType.setId( petTypeDto.getId() );
+        petType.setName( petTypeDto.getName() );
+
+        return petType;
+    }
+
+    @Override
+    public PetType toPetType(PetTypeFieldsDto petTypeFieldsDto) {
+        if ( petTypeFieldsDto == null ) {
+            return null;
+        }
+
+        PetType petType = new PetType();
+
+        petType.setName( petTypeFieldsDto.getName() );
+
+        return petType;
+    }
+
+    @Override
+    public PetTypeDto toPetTypeDto(PetType petType) {
+        if ( petType == null ) {
+            return null;
+        }
+
+        PetTypeDto petTypeDto = new PetTypeDto();
+
+        petTypeDto.setName( petType.getName() );
+        petTypeDto.setId( petType.getId() );
+
+        return petTypeDto;
+    }
+
+    @Override
+    public List<PetTypeDto> toPetTypeDtos(Collection<PetType> petTypes) {
+        if ( petTypes == null ) {
+            return null;
+        }
+
+        List<PetTypeDto> list = new ArrayList<PetTypeDto>( petTypes.size() );
+        for ( PetType petType : petTypes ) {
+            list.add( toPetTypeDto( petType ) );
+        }
+
+        return list;
+    }
+}

--- a/SpecialtyMapperImpl.java
+++ b/SpecialtyMapperImpl.java
@@ -0,0 +1,71 @@
+package org.springframework.samples.petclinic.mapper;
+
+import java.util.ArrayList;
+import java.util.Collection;
+import javax.annotation.processing.Generated;
+import org.springframework.samples.petclinic.model.Specialty;
+import org.springframework.samples.petclinic.rest.dto.SpecialtyDto;
+import org.springframework.stereotype.Component;
+
+@Generated(
+    value = "org.mapstruct.ap.MappingProcessor"
+)
+@Component
+public class SpecialtyMapperImpl implements SpecialtyMapper {
+
+    @Override
+    public Specialty toSpecialty(SpecialtyDto specialtyDto) {
+        if ( specialtyDto == null ) {
+            return null;
+        }
+
+        Specialty specialty = new Specialty();
+
+        specialty.setId( specialtyDto.getId() );
+        specialty.setName( specialtyDto.getName() );
+
+        return specialty;
+    }
+
+    @Override
+    public SpecialtyDto toSpecialtyDto(Specialty specialty) {
+        if ( specialty == null ) {
+            return null;
+        }
+
+        SpecialtyDto specialtyDto = new SpecialtyDto();
+
+        specialtyDto.setId( specialty.getId() );
+        specialtyDto.setName( specialty.getName() );
+
+        return specialtyDto;
+    }
+
+    @Override
+    public Collection<SpecialtyDto> toSpecialtyDtos(Collection<Specialty> specialties) {
+        if ( specialties == null ) {
+            return null;
+        }
+
+        Collection<SpecialtyDto> collection = new ArrayList<SpecialtyDto>( specialties.size() );
+        for ( Specialty specialty : specialties ) {
+            collection.add( toSpecialtyDto( specialty ) );
+        }
+
+        return collection;
+    }
+
+    @Override
+    public Collection<Specialty> toSpecialtys(Collection<SpecialtyDto> specialties) {
+        if ( specialties == null ) {
+            return null;
+        }
+
+        Collection<Specialty> collection = new ArrayList<Specialty>( specialties.size() );
+        for ( SpecialtyDto specialtyDto : specialties ) {
+            collection.add( toSpecialty( specialtyDto ) );
+        }
+
+        return collection;
+    }
+}

--- a/UserMapperImpl.java
+++ b/UserMapperImpl.java
@@ -0,0 +1,132 @@
+package org.springframework.samples.petclinic.mapper;
+
+import java.util.ArrayList;
+import java.util.Collection;
+import java.util.LinkedHashSet;
+import java.util.List;
+import java.util.Set;
+import javax.annotation.processing.Generated;
+import org.springframework.samples.petclinic.model.Role;
+import org.springframework.samples.petclinic.model.User;
+import org.springframework.samples.petclinic.rest.dto.RoleDto;
+import org.springframework.samples.petclinic.rest.dto.UserDto;
+import org.springframework.stereotype.Component;
+
+@Generated(
+    value = "org.mapstruct.ap.MappingProcessor"
+)
+@Component
+public class UserMapperImpl implements UserMapper {
+
+    @Override
+    public Role toRole(RoleDto roleDto) {
+        if ( roleDto == null ) {
+            return null;
+        }
+
+        Role role = new Role();
+
+        role.setName( roleDto.getName() );
+
+        return role;
+    }
+
+    @Override
+    public RoleDto toRoleDto(Role role) {
+        if ( role == null ) {
+            return null;
+        }
+
+        RoleDto roleDto = new RoleDto();
+
+        roleDto.setName( role.getName() );
+
+        return roleDto;
+    }
+
+    @Override
+    public Collection<RoleDto> toRoleDtos(Collection<Role> roles) {
+        if ( roles == null ) {
+            return null;
+        }
+
+        Collection<RoleDto> collection = new ArrayList<RoleDto>( roles.size() );
+        for ( Role role : roles ) {
+            collection.add( toRoleDto( role ) );
+        }
+
+        return collection;
+    }
+
+    @Override
+    public User toUser(UserDto userDto) {
+        if ( userDto == null ) {
+            return null;
+        }
+
+        User user = new User();
+
+        user.setUsername( userDto.getUsername() );
+        user.setPassword( userDto.getPassword() );
+        user.setEnabled( userDto.getEnabled() );
+        user.setRoles( roleDtoListToRoleSet( userDto.getRoles() ) );
+
+        return user;
+    }
+
+    @Override
+    public UserDto toUserDto(User user) {
+        if ( user == null ) {
+            return null;
+        }
+
+        UserDto userDto = new UserDto();
+
+        userDto.setUsername( user.getUsername() );
+        userDto.setPassword( user.getPassword() );
+        userDto.setEnabled( user.getEnabled() );
+        userDto.setRoles( roleSetToRoleDtoList( user.getRoles() ) );
+
+        return userDto;
+    }
+
+    @Override
+    public Collection<Role> toRoles(Collection<RoleDto> roleDtos) {
+        if ( roleDtos == null ) {
+            return null;
+        }
+
+        Collection<Role> collection = new ArrayList<Role>( roleDtos.size() );
+        for ( RoleDto roleDto : roleDtos ) {
+            collection.add( toRole( roleDto ) );
+        }
+
+        return collection;
+    }
+
+    protected Set<Role> roleDtoListToRoleSet(List<RoleDto> list) {
+        if ( list == null ) {
+            return null;
+        }
+
+        Set<Role> set = new LinkedHashSet<Role>( Math.max( (int) ( list.size() / .75f ) + 1, 16 ) );
+        for ( RoleDto roleDto : list ) {
+            set.add( toRole( roleDto ) );
+        }
+
+        return set;
+    }
+
+    protected List<RoleDto> roleSetToRoleDtoList(Set<Role> set) {
+        if ( set == null ) {
+            return null;
+        }
+
+        List<RoleDto> list = new ArrayList<RoleDto>( set.size() );
+        for ( Role role : set ) {
+            list.add( toRoleDto( role ) );
+        }
+
+        return list;
+    }
+}

--- a/VetMapperImpl.java
+++ b/VetMapperImpl.java
@@ -0,0 +1,110 @@
+package org.springframework.samples.petclinic.mapper;
+
+import java.util.ArrayList;
+import java.util.Collection;
+import java.util.List;
+import javax.annotation.processing.Generated;
+import org.springframework.beans.factory.annotation.Autowired;
+import org.springframework.samples.petclinic.model.Specialty;
+import org.springframework.samples.petclinic.model.Vet;
+import org.springframework.samples.petclinic.rest.dto.SpecialtyDto;
+import org.springframework.samples.petclinic.rest.dto.VetDto;
+import org.springframework.samples.petclinic.rest.dto.VetFieldsDto;
+import org.springframework.stereotype.Component;
+
+@Generated(
+    value = "org.mapstruct.ap.MappingProcessor"
+)
+@Component
+public class VetMapperImpl implements VetMapper {
+
+    @Autowired
+    private SpecialtyMapper specialtyMapper;
+
+    @Override
+    public Vet toVet(VetDto vetDto) {
+        if ( vetDto == null ) {
+            return null;
+        }
+
+        Vet vet = new Vet();
+
+        vet.setId( vetDto.getId() );
+        vet.setFirstName( vetDto.getFirstName() );
+        vet.setLastName( vetDto.getLastName() );
+        vet.setSpecialties( specialtyDtoListToSpecialtyList( vetDto.getSpecialties() ) );
+
+        return vet;
+    }
+
+    @Override
+    public Vet toVet(VetFieldsDto vetFieldsDto) {
+        if ( vetFieldsDto == null ) {
+            return null;
+        }
+
+        Vet vet = new Vet();
+
+        vet.setFirstName( vetFieldsDto.getFirstName() );
+        vet.setLastName( vetFieldsDto.getLastName() );
+        vet.setSpecialties( specialtyDtoListToSpecialtyList( vetFieldsDto.getSpecialties() ) );
+
+        return vet;
+    }
+
+    @Override
+    public VetDto toVetDto(Vet vet) {
+        if ( vet == null ) {
+            return null;
+        }
+
+        VetDto vetDto = new VetDto();
+
+        vetDto.setFirstName( vet.getFirstName() );
+        vetDto.setLastName( vet.getLastName() );
+        vetDto.setSpecialties( specialtyListToSpecialtyDtoList( vet.getSpecialties() ) );
+        vetDto.setId( vet.getId() );
+
+        return vetDto;
+    }
+
+    @Override
+    public Collection<VetDto> toVetDtos(Collection<Vet> vets) {
+        if ( vets == null ) {
+            return null;
+        }
+
+        Collection<VetDto> collection = new ArrayList<VetDto>( vets.size() );
+        for ( Vet vet : vets ) {
+            collection.add( toVetDto( vet ) );
+        }
+
+        return collection;
+    }
+
+    protected List<Specialty> specialtyDtoListToSpecialtyList(List<SpecialtyDto> list) {
+        if ( list == null ) {
+            return null;
+        }
+
+        List<Specialty> list1 = new ArrayList<Specialty>( list.size() );
+        for ( SpecialtyDto specialtyDto : list ) {
+            list1.add( specialtyMapper.toSpecialty( specialtyDto ) );
+        }
+
+        return list1;
+    }
+
+    protected List<SpecialtyDto> specialtyListToSpecialtyDtoList(List<Specialty> list) {
+        if ( list == null ) {
+            return null;
+        }
+
+        List<SpecialtyDto> list1 = new ArrayList<SpecialtyDto>( list.size() );
+        for ( Specialty specialty : list ) {
+            list1.add( specialtyMapper.toSpecialtyDto( specialty ) );
+        }
+
+        return list1;
+    }
+}

--- a/VisitMapperImpl.java
+++ b/VisitMapperImpl.java
@@ -0,0 +1,84 @@
+package org.springframework.samples.petclinic.mapper;
+
+import java.util.ArrayList;
+import java.util.Collection;
+import javax.annotation.processing.Generated;
+import org.springframework.samples.petclinic.model.Pet;
+import org.springframework.samples.petclinic.model.Visit;
+import org.springframework.samples.petclinic.rest.dto.VisitDto;
+import org.springframework.samples.petclinic.rest.dto.VisitFieldsDto;
+import org.springframework.stereotype.Component;
+
+@Generated(
+    value = "org.mapstruct.ap.MappingProcessor"
+)
+@Component
+public class VisitMapperImpl implements VisitMapper {
+
+    @Override
+    public Visit toVisit(VisitDto visitDto) {
+        if ( visitDto == null ) {
+            return null;
+        }
+
+        Visit visit = new Visit();
+
+        visit.setId( visitDto.getId() );
+        visit.setDate( visitDto.getDate() );
+        visit.setDescription( visitDto.getDescription() );
+
+        return visit;
+    }
+
+    @Override
+    public Visit toVisit(VisitFieldsDto visitFieldsDto) {
+        if ( visitFieldsDto == null ) {
+            return null;
+        }
+
+        Visit visit = new Visit();
+
+        visit.setDate( visitFieldsDto.getDate() );
+        visit.setDescription( visitFieldsDto.getDescription() );
+
+        return visit;
+    }
+
+    @Override
+    public VisitDto toVisitDto(Visit visit) {
+        if ( visit == null ) {
+            return null;
+        }
+
+        VisitDto visitDto = new VisitDto();
+
+        visitDto.setPetId( visitPetId( visit ) );
+        visitDto.setDate( visit.getDate() );
+        visitDto.setDescription( visit.getDescription() );
+        visitDto.setId( visit.getId() );
+
+        return visitDto;
+    }
+
+    @Override
+    public Collection<VisitDto> toVisitsDto(Collection<Visit> visits) {
+        if ( visits == null ) {
+            return null;
+        }
+
+        Collection<VisitDto> collection = new ArrayList<VisitDto>( visits.size() );
+        for ( Visit visit : visits ) {
+            collection.add( toVisitDto( visit ) );
+        }
+
+        return collection;
+    }
+
+    private Integer visitPetId(Visit visit) {
+        Pet pet = visit.getPet();
+        if ( pet == null ) {
+            return null;
+        }
+        return pet.getId();
+    }
+}

--- a/ApiUtil.java
+++ b/ApiUtil.java
@@ -0,0 +1,19 @@
+package org.springframework.samples.petclinic.rest.api;
+
+import org.springframework.web.context.request.NativeWebRequest;
+
+import javax.servlet.http.HttpServletResponse;
+import java.io.IOException;
+
+public class ApiUtil {
+    public static void setExampleResponse(NativeWebRequest req, String contentType, String example) {
+        try {
+            HttpServletResponse res = req.getNativeResponse(HttpServletResponse.class);
+            res.setCharacterEncoding("UTF-8");
+            res.addHeader("Content-Type", contentType);
+            res.getWriter().print(example);
+        } catch (IOException e) {
+            throw new RuntimeException(e);
+        }
+    }
+}

--- a/OopsApi.java
+++ b/OopsApi.java
@@ -0,0 +1,77 @@
+/**
+ * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.0.1).
+ * https://openapi-generator.tech
+ * Do not edit the class manually.
+ */
+package org.springframework.samples.petclinic.rest.api;
+
+import org.springframework.samples.petclinic.rest.dto.RestErrorDto;
+import io.swagger.v3.oas.annotations.Operation;
+import io.swagger.v3.oas.annotations.Parameter;
+import io.swagger.v3.oas.annotations.Parameters;
+import io.swagger.v3.oas.annotations.media.Content;
+import io.swagger.v3.oas.annotations.media.Schema;
+import io.swagger.v3.oas.annotations.responses.ApiResponse;
+import io.swagger.v3.oas.annotations.security.SecurityRequirement;
+import io.swagger.v3.oas.annotations.tags.Tag;
+import org.springframework.http.HttpStatus;
+import org.springframework.http.MediaType;
+import org.springframework.http.ResponseEntity;
+import org.springframework.validation.annotation.Validated;
+import org.springframework.web.bind.annotation.*;
+import org.springframework.web.context.request.NativeWebRequest;
+import org.springframework.web.multipart.MultipartFile;
+
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import javax.annotation.Generated;
+
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+@Validated
+@Tag(name = "oops", description = "Endpoint which always returns an error.")
+public interface OopsApi {
+
+    default Optional<NativeWebRequest> getRequest() {
+        return Optional.empty();
+    }
+
+    /**
+     * GET /oops : Always fails
+     * Produces sample error response.
+     *
+     * @return Never returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     */
+    @Operation(
+        operationId = "failingRequest",
+        summary = "Always fails",
+        tags = { "failing" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Never returned.", content = {
+                @Content(mediaType = "text/plain", schema = @Schema(implementation = String.class)),
+                @Content(mediaType = "application/json", schema = @Schema(implementation = String.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "text/plain", schema = @Schema(implementation = RestErrorDto.class)),
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.GET,
+        value = "/oops",
+        produces = { "text/plain", "application/json" }
+    )
+    default ResponseEntity<String> failingRequest(
+        
+    ) {
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+}

--- a/OwnersApi.java
+++ b/OwnersApi.java
@@ -0,0 +1,509 @@
+/**
+ * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.0.1).
+ * https://openapi-generator.tech
+ * Do not edit the class manually.
+ */
+package org.springframework.samples.petclinic.rest.api;
+
+import org.springframework.samples.petclinic.rest.dto.OwnerDto;
+import org.springframework.samples.petclinic.rest.dto.OwnerFieldsDto;
+import org.springframework.samples.petclinic.rest.dto.PetDto;
+import org.springframework.samples.petclinic.rest.dto.PetFieldsDto;
+import org.springframework.samples.petclinic.rest.dto.RestErrorDto;
+import org.springframework.samples.petclinic.rest.dto.VisitDto;
+import org.springframework.samples.petclinic.rest.dto.VisitFieldsDto;
+import io.swagger.v3.oas.annotations.Operation;
+import io.swagger.v3.oas.annotations.Parameter;
+import io.swagger.v3.oas.annotations.Parameters;
+import io.swagger.v3.oas.annotations.media.Content;
+import io.swagger.v3.oas.annotations.media.Schema;
+import io.swagger.v3.oas.annotations.responses.ApiResponse;
+import io.swagger.v3.oas.annotations.security.SecurityRequirement;
+import io.swagger.v3.oas.annotations.tags.Tag;
+import org.springframework.http.HttpStatus;
+import org.springframework.http.MediaType;
+import org.springframework.http.ResponseEntity;
+import org.springframework.validation.annotation.Validated;
+import org.springframework.web.bind.annotation.*;
+import org.springframework.web.context.request.NativeWebRequest;
+import org.springframework.web.multipart.MultipartFile;
+
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import javax.annotation.Generated;
+
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+@Validated
+@Tag(name = "owners", description = "Endpoints related to pet owners.")
+public interface OwnersApi {
+
+    default Optional<NativeWebRequest> getRequest() {
+        return Optional.empty();
+    }
+
+    /**
+     * POST /owners : Adds a pet owner
+     * Records the details of a new pet owner.
+     *
+     * @param ownerFieldsDto The pet owner (required)
+     * @return The pet owner was sucessfully added. (status code 201)
+     *         or Bad request. (status code 400)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "addOwner",
+        summary = "Adds a pet owner",
+        tags = { "owner" },
+        responses = {
+            @ApiResponse(responseCode = "201", description = "The pet owner was sucessfully added.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = OwnerDto.class))
+            }),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.POST,
+        value = "/owners",
+        produces = { "application/json" },
+        consumes = { "application/json" }
+    )
+    default ResponseEntity<OwnerDto> addOwner(
+        @Parameter(name = "OwnerFieldsDto", description = "The pet owner", required = true) @Valid @RequestBody OwnerFieldsDto ownerFieldsDto
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * POST /owners/{ownerId}/pets : Adds a pet to an owner
+     * Records the details of a new pet.
+     *
+     * @param ownerId The ID of the pet owner. (required)
+     * @param petFieldsDto The details of the new pet. (required)
+     * @return The pet was sucessfully added. (status code 201)
+     *         or Bad request. (status code 400)
+     *         or Pet not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "addPetToOwner",
+        summary = "Adds a pet to an owner",
+        tags = { "pet" },
+        responses = {
+            @ApiResponse(responseCode = "201", description = "The pet was sucessfully added.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = PetDto.class))
+            }),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Pet not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.POST,
+        value = "/owners/{ownerId}/pets",
+        produces = { "application/json" },
+        consumes = { "application/json" }
+    )
+    default ResponseEntity<PetDto> addPetToOwner(
+        @Min(0) @Parameter(name = "ownerId", description = "The ID of the pet owner.", required = true) @PathVariable("ownerId") Integer ownerId,
+        @Parameter(name = "PetFieldsDto", description = "The details of the new pet.", required = true) @Valid @RequestBody PetFieldsDto petFieldsDto
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * POST /owners/{ownerId}/pets/{petId}/visits : Adds a vet visit
+     * Records the details of a new vet visit.
+     *
+     * @param ownerId The ID of the pet owner. (required)
+     * @param petId The ID of the pet. (required)
+     * @param visitFieldsDto The details of the new vet visit. (required)
+     * @return The vet visit was sucessfully added. (status code 201)
+     *         or Bad request. (status code 400)
+     *         or Pet not found for this owner. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "addVisitToOwner",
+        summary = "Adds a vet visit",
+        tags = { "visit" },
+        responses = {
+            @ApiResponse(responseCode = "201", description = "The vet visit was sucessfully added.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = VisitDto.class))
+            }),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Pet not found for this owner.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.POST,
+        value = "/owners/{ownerId}/pets/{petId}/visits",
+        produces = { "application/json" },
+        consumes = { "application/json" }
+    )
+    default ResponseEntity<VisitDto> addVisitToOwner(
+        @Min(0) @Parameter(name = "ownerId", description = "The ID of the pet owner.", required = true) @PathVariable("ownerId") Integer ownerId,
+        @Min(0) @Parameter(name = "petId", description = "The ID of the pet.", required = true) @PathVariable("petId") Integer petId,
+        @Parameter(name = "VisitFieldsDto", description = "The details of the new vet visit.", required = true) @Valid @RequestBody VisitFieldsDto visitFieldsDto
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * DELETE /owners/{ownerId} : Delete an owner by ID
+     * Returns the owner or a 404 error.
+     *
+     * @param ownerId The ID of the owner. (required)
+     * @return Owner details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Owner  not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "deleteOwner",
+        summary = "Delete an owner by ID",
+        tags = { "owner" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Owner details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = OwnerDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Owner  not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.DELETE,
+        value = "/owners/{ownerId}",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<OwnerDto> deleteOwner(
+        @Min(0) @Parameter(name = "ownerId", description = "The ID of the owner.", required = true) @PathVariable("ownerId") Integer ownerId
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * GET /owners/{ownerId} : Get a pet owner by ID
+     * Returns the pet owner or a 404 error.
+     *
+     * @param ownerId The ID of the pet owner. (required)
+     * @return Owner details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Owner not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "getOwner",
+        summary = "Get a pet owner by ID",
+        tags = { "owner" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Owner details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = OwnerDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Owner not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.GET,
+        value = "/owners/{ownerId}",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<OwnerDto> getOwner(
+        @Min(0) @Parameter(name = "ownerId", description = "The ID of the pet owner.", required = true) @PathVariable("ownerId") Integer ownerId
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * GET /owners/{ownerId}/pets/{petId} : Get a pet by ID
+     * Returns the pet or a 404 error.
+     *
+     * @param ownerId The ID of the pet owner. (required)
+     * @param petId The ID of the pet. (required)
+     * @return Pet details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Pet not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "getOwnersPet",
+        summary = "Get a pet by ID",
+        tags = { "pet" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Pet details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = PetDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Pet not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.GET,
+        value = "/owners/{ownerId}/pets/{petId}",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<PetDto> getOwnersPet(
+        @Min(0) @Parameter(name = "ownerId", description = "The ID of the pet owner.", required = true) @PathVariable("ownerId") Integer ownerId,
+        @Min(0) @Parameter(name = "petId", description = "The ID of the pet.", required = true) @PathVariable("petId") Integer petId
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * GET /owners : Lists pet owners
+     * Returns an array of pet owners.
+     *
+     * @param lastName Last name. (optional)
+     * @return Owner details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "listOwners",
+        summary = "Lists pet owners",
+        tags = { "owner" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Owner details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = OwnerDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.GET,
+        value = "/owners",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<List<OwnerDto>> listOwners(
+        @Parameter(name = "lastName", description = "Last name.") @Valid @RequestParam(value = "lastName", required = false) String lastName
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * PUT /owners/{ownerId} : Update a pet owner&#39;s details
+     * Updates the pet owner record with the specified details.
+     *
+     * @param ownerId The ID of the pet owner. (required)
+     * @param ownerFieldsDto The pet owner details to use for the update. (required)
+     * @return Update successful. (status code 200)
+     *         or Bad request. (status code 400)
+     *         or Owner not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "updateOwner",
+        summary = "Update a pet owner's details",
+        tags = { "owner" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Update successful.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = OwnerDto.class))
+            }),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Owner not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.PUT,
+        value = "/owners/{ownerId}",
+        produces = { "application/json" },
+        consumes = { "application/json" }
+    )
+    default ResponseEntity<OwnerDto> updateOwner(
+        @Min(0) @Parameter(name = "ownerId", description = "The ID of the pet owner.", required = true) @PathVariable("ownerId") Integer ownerId,
+        @Parameter(name = "OwnerFieldsDto", description = "The pet owner details to use for the update.", required = true) @Valid @RequestBody OwnerFieldsDto ownerFieldsDto
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * PUT /owners/{ownerId}/pets/{petId} : Update a pet&#39;s details
+     * Updates the pet record with the specified details.
+     *
+     * @param ownerId The ID of the pet owner. (required)
+     * @param petId The ID of the pet. (required)
+     * @param petFieldsDto The pet details to use for the update. (required)
+     * @return Update successful. (status code 204)
+     *         or Bad request. (status code 400)
+     *         or Pet not found for this owner. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "updateOwnersPet",
+        summary = "Update a pet's details",
+        tags = { "pet" },
+        responses = {
+            @ApiResponse(responseCode = "204", description = "Update successful."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Pet not found for this owner.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.PUT,
+        value = "/owners/{ownerId}/pets/{petId}",
+        produces = { "application/json" },
+        consumes = { "application/json" }
+    )
+    default ResponseEntity<Void> updateOwnersPet(
+        @Min(0) @Parameter(name = "ownerId", description = "The ID of the pet owner.", required = true) @PathVariable("ownerId") Integer ownerId,
+        @Min(0) @Parameter(name = "petId", description = "The ID of the pet.", required = true) @PathVariable("petId") Integer petId,
+        @Parameter(name = "PetFieldsDto", description = "The pet details to use for the update.", required = true) @Valid @RequestBody PetFieldsDto petFieldsDto
+    ) {
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+}

--- a/PetsApi.java
+++ b/PetsApi.java
@@ -0,0 +1,301 @@
+/**
+ * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.0.1).
+ * https://openapi-generator.tech
+ * Do not edit the class manually.
+ */
+package org.springframework.samples.petclinic.rest.api;
+
+import org.springframework.samples.petclinic.rest.dto.PetDto;
+import org.springframework.samples.petclinic.rest.dto.RestErrorDto;
+import io.swagger.v3.oas.annotations.Operation;
+import io.swagger.v3.oas.annotations.Parameter;
+import io.swagger.v3.oas.annotations.Parameters;
+import io.swagger.v3.oas.annotations.media.Content;
+import io.swagger.v3.oas.annotations.media.Schema;
+import io.swagger.v3.oas.annotations.responses.ApiResponse;
+import io.swagger.v3.oas.annotations.security.SecurityRequirement;
+import io.swagger.v3.oas.annotations.tags.Tag;
+import org.springframework.http.HttpStatus;
+import org.springframework.http.MediaType;
+import org.springframework.http.ResponseEntity;
+import org.springframework.validation.annotation.Validated;
+import org.springframework.web.bind.annotation.*;
+import org.springframework.web.context.request.NativeWebRequest;
+import org.springframework.web.multipart.MultipartFile;
+
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import javax.annotation.Generated;
+
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+@Validated
+@Tag(name = "pets", description = "Endpoints related to pets.")
+public interface PetsApi {
+
+    default Optional<NativeWebRequest> getRequest() {
+        return Optional.empty();
+    }
+
+    /**
+     * POST /pets : Create a pet
+     * Creates a pet .
+     *
+     * @param petDto The pet (required)
+     * @return Pet type created successfully. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Pet not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "addPet",
+        summary = "Create a pet",
+        tags = { "pet" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Pet type created successfully.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = PetDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Pet not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.POST,
+        value = "/pets",
+        produces = { "application/json" },
+        consumes = { "application/json" }
+    )
+    default ResponseEntity<PetDto> addPet(
+        @Parameter(name = "PetDto", description = "The pet", required = true) @Valid @RequestBody PetDto petDto
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * DELETE /pets/{petId} : Delete a pet by ID
+     * Returns the pet or a 404 error.
+     *
+     * @param petId The ID of the pet. (required)
+     * @return Pet details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Pet not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "deletePet",
+        summary = "Delete a pet by ID",
+        tags = { "pet" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Pet details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = PetDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Pet not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.DELETE,
+        value = "/pets/{petId}",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<PetDto> deletePet(
+        @Min(0) @Parameter(name = "petId", description = "The ID of the pet.", required = true) @PathVariable("petId") Integer petId
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * GET /pets/{petId} : Get a pet by ID
+     * Returns the pet  or a 404 error.
+     *
+     * @param petId The ID of the pet. (required)
+     * @return Pet details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Pet not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "getPet",
+        summary = "Get a pet by ID",
+        tags = { "pet" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Pet details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = PetDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Pet not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.GET,
+        value = "/pets/{petId}",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<PetDto> getPet(
+        @Min(0) @Parameter(name = "petId", description = "The ID of the pet.", required = true) @PathVariable("petId") Integer petId
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * GET /pets : Lists pet
+     * Returns an array of pet .
+     *
+     * @return Pet types found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "listPets",
+        summary = "Lists pet",
+        tags = { "pet" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Pet types found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = PetDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.GET,
+        value = "/pets",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<List<PetDto>> listPets(
+        
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * PUT /pets/{petId} : Update a pet by ID
+     * Returns the pet or a 404 error.
+     *
+     * @param petId The ID of the pet. (required)
+     * @param petDto The pet (required)
+     * @return Pet details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Pet not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "updatePet",
+        summary = "Update a pet by ID",
+        tags = { "pet" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Pet details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = PetDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Pet not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.PUT,
+        value = "/pets/{petId}",
+        produces = { "application/json" },
+        consumes = { "application/json" }
+    )
+    default ResponseEntity<PetDto> updatePet(
+        @Min(0) @Parameter(name = "petId", description = "The ID of the pet.", required = true) @PathVariable("petId") Integer petId,
+        @Parameter(name = "PetDto", description = "The pet", required = true) @Valid @RequestBody PetDto petDto
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+}

--- a/PettypesApi.java
+++ b/PettypesApi.java
@@ -0,0 +1,301 @@
+/**
+ * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.0.1).
+ * https://openapi-generator.tech
+ * Do not edit the class manually.
+ */
+package org.springframework.samples.petclinic.rest.api;
+
+import org.springframework.samples.petclinic.rest.dto.PetTypeDto;
+import org.springframework.samples.petclinic.rest.dto.RestErrorDto;
+import io.swagger.v3.oas.annotations.Operation;
+import io.swagger.v3.oas.annotations.Parameter;
+import io.swagger.v3.oas.annotations.Parameters;
+import io.swagger.v3.oas.annotations.media.Content;
+import io.swagger.v3.oas.annotations.media.Schema;
+import io.swagger.v3.oas.annotations.responses.ApiResponse;
+import io.swagger.v3.oas.annotations.security.SecurityRequirement;
+import io.swagger.v3.oas.annotations.tags.Tag;
+import org.springframework.http.HttpStatus;
+import org.springframework.http.MediaType;
+import org.springframework.http.ResponseEntity;
+import org.springframework.validation.annotation.Validated;
+import org.springframework.web.bind.annotation.*;
+import org.springframework.web.context.request.NativeWebRequest;
+import org.springframework.web.multipart.MultipartFile;
+
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import javax.annotation.Generated;
+
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+@Validated
+@Tag(name = "pettypes", description = "the pettypes API")
+public interface PettypesApi {
+
+    default Optional<NativeWebRequest> getRequest() {
+        return Optional.empty();
+    }
+
+    /**
+     * POST /pettypes : Create a pet type
+     * Creates a pet type .
+     *
+     * @param petTypeDto The pet type (required)
+     * @return Pet type created successfully. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Pet Type not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "addPetType",
+        summary = "Create a pet type",
+        tags = { "pettypes" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Pet type created successfully.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = PetTypeDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Pet Type not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.POST,
+        value = "/pettypes",
+        produces = { "application/json" },
+        consumes = { "application/json" }
+    )
+    default ResponseEntity<PetTypeDto> addPetType(
+        @Parameter(name = "PetTypeDto", description = "The pet type", required = true) @Valid @RequestBody PetTypeDto petTypeDto
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * DELETE /pettypes/{petTypeId} : Delete a pet type by ID
+     * Returns the pet type or a 404 error.
+     *
+     * @param petTypeId The ID of the pet type. (required)
+     * @return Pet type details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Pet type not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "deletePetType",
+        summary = "Delete a pet type by ID",
+        tags = { "pettypes" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Pet type details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = PetTypeDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Pet type not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.DELETE,
+        value = "/pettypes/{petTypeId}",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<PetTypeDto> deletePetType(
+        @Min(0) @Parameter(name = "petTypeId", description = "The ID of the pet type.", required = true) @PathVariable("petTypeId") Integer petTypeId
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * GET /pettypes/{petTypeId} : Get a pet type by ID
+     * Returns the pet type or a 404 error.
+     *
+     * @param petTypeId The ID of the pet type. (required)
+     * @return Pet type details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Pet Type not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "getPetType",
+        summary = "Get a pet type by ID",
+        tags = { "pettypes" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Pet type details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = PetTypeDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Pet Type not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.GET,
+        value = "/pettypes/{petTypeId}",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<PetTypeDto> getPetType(
+        @Min(0) @Parameter(name = "petTypeId", description = "The ID of the pet type.", required = true) @PathVariable("petTypeId") Integer petTypeId
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * GET /pettypes : Lists pet types
+     * Returns an array of pet types.
+     *
+     * @return Pet types found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "listPetTypes",
+        summary = "Lists pet types",
+        tags = { "pettypes" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Pet types found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = PetTypeDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.GET,
+        value = "/pettypes",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<List<PetTypeDto>> listPetTypes(
+        
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * PUT /pettypes/{petTypeId} : Update a pet type by ID
+     * Returns the pet type or a 404 error.
+     *
+     * @param petTypeId The ID of the pet type. (required)
+     * @param petTypeDto The pet type (required)
+     * @return Pet type details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Pet Type not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "updatePetType",
+        summary = "Update a pet type by ID",
+        tags = { "pettypes" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Pet type details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = PetTypeDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Pet Type not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.PUT,
+        value = "/pettypes/{petTypeId}",
+        produces = { "application/json" },
+        consumes = { "application/json" }
+    )
+    default ResponseEntity<PetTypeDto> updatePetType(
+        @Min(0) @Parameter(name = "petTypeId", description = "The ID of the pet type.", required = true) @PathVariable("petTypeId") Integer petTypeId,
+        @Parameter(name = "PetTypeDto", description = "The pet type", required = true) @Valid @RequestBody PetTypeDto petTypeDto
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+}

--- a/SpecialtiesApi.java
+++ b/SpecialtiesApi.java
@@ -0,0 +1,301 @@
+/**
+ * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.0.1).
+ * https://openapi-generator.tech
+ * Do not edit the class manually.
+ */
+package org.springframework.samples.petclinic.rest.api;
+
+import org.springframework.samples.petclinic.rest.dto.RestErrorDto;
+import org.springframework.samples.petclinic.rest.dto.SpecialtyDto;
+import io.swagger.v3.oas.annotations.Operation;
+import io.swagger.v3.oas.annotations.Parameter;
+import io.swagger.v3.oas.annotations.Parameters;
+import io.swagger.v3.oas.annotations.media.Content;
+import io.swagger.v3.oas.annotations.media.Schema;
+import io.swagger.v3.oas.annotations.responses.ApiResponse;
+import io.swagger.v3.oas.annotations.security.SecurityRequirement;
+import io.swagger.v3.oas.annotations.tags.Tag;
+import org.springframework.http.HttpStatus;
+import org.springframework.http.MediaType;
+import org.springframework.http.ResponseEntity;
+import org.springframework.validation.annotation.Validated;
+import org.springframework.web.bind.annotation.*;
+import org.springframework.web.context.request.NativeWebRequest;
+import org.springframework.web.multipart.MultipartFile;
+
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import javax.annotation.Generated;
+
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+@Validated
+@Tag(name = "specialties", description = "the specialties API")
+public interface SpecialtiesApi {
+
+    default Optional<NativeWebRequest> getRequest() {
+        return Optional.empty();
+    }
+
+    /**
+     * POST /specialties : Create a specialty
+     * Creates a specialty .
+     *
+     * @param specialtyDto The specialty (required)
+     * @return Specialty created successfully. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Specialty not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "addSpecialty",
+        summary = "Create a specialty",
+        tags = { "specialty" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Specialty created successfully.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = SpecialtyDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Specialty not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.POST,
+        value = "/specialties",
+        produces = { "application/json" },
+        consumes = { "application/json" }
+    )
+    default ResponseEntity<SpecialtyDto> addSpecialty(
+        @Parameter(name = "SpecialtyDto", description = "The specialty", required = true) @Valid @RequestBody SpecialtyDto specialtyDto
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "{ \"name\" : \"radiology\", \"id\" : 1 }";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * DELETE /specialties/{specialtyId} : Delete a specialty by ID
+     * Returns the specialty or a 404 error.
+     *
+     * @param specialtyId The ID of the specialty. (required)
+     * @return Specialty details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Specialty not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "deleteSpecialty",
+        summary = "Delete a specialty by ID",
+        tags = { "specialty" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Specialty details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = SpecialtyDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Specialty not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.DELETE,
+        value = "/specialties/{specialtyId}",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<SpecialtyDto> deleteSpecialty(
+        @Min(0) @Parameter(name = "specialtyId", description = "The ID of the specialty.", required = true) @PathVariable("specialtyId") Integer specialtyId
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "{ \"name\" : \"radiology\", \"id\" : 1 }";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * GET /specialties/{specialtyId} : Get a specialty by ID
+     * Returns the specialty or a 404 error.
+     *
+     * @param specialtyId The ID of the pet. (required)
+     * @return Specialty details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Specialty not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "getSpecialty",
+        summary = "Get a specialty by ID",
+        tags = { "specialty" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Specialty details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = SpecialtyDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Specialty not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.GET,
+        value = "/specialties/{specialtyId}",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<SpecialtyDto> getSpecialty(
+        @Min(0) @Parameter(name = "specialtyId", description = "The ID of the pet.", required = true) @PathVariable("specialtyId") Integer specialtyId
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "{ \"name\" : \"radiology\", \"id\" : 1 }";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * GET /specialties : Lists specialties
+     * Returns an array of specialty .
+     *
+     * @return Specialties found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "listSpecialties",
+        summary = "Lists specialties",
+        tags = { "specialty" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Specialties found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = SpecialtyDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.GET,
+        value = "/specialties",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<List<SpecialtyDto>> listSpecialties(
+        
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "{ \"name\" : \"radiology\", \"id\" : 1 }";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * PUT /specialties/{specialtyId} : Update a specialty by ID
+     * Returns the specialty or a 404 error.
+     *
+     * @param specialtyId The ID of the specialty. (required)
+     * @param specialtyDto The pet (required)
+     * @return Specialty details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Specialty not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "updateSpecialty",
+        summary = "Update a specialty by ID",
+        tags = { "specialty" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Specialty details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = SpecialtyDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Specialty not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.PUT,
+        value = "/specialties/{specialtyId}",
+        produces = { "application/json" },
+        consumes = { "application/json" }
+    )
+    default ResponseEntity<SpecialtyDto> updateSpecialty(
+        @Min(0) @Parameter(name = "specialtyId", description = "The ID of the specialty.", required = true) @PathVariable("specialtyId") Integer specialtyId,
+        @Parameter(name = "SpecialtyDto", description = "The pet", required = true) @Valid @RequestBody SpecialtyDto specialtyDto
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "{ \"name\" : \"radiology\", \"id\" : 1 }";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+}

--- a/UsersApi.java
+++ b/UsersApi.java
@@ -0,0 +1,95 @@
+/**
+ * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.0.1).
+ * https://openapi-generator.tech
+ * Do not edit the class manually.
+ */
+package org.springframework.samples.petclinic.rest.api;
+
+import org.springframework.samples.petclinic.rest.dto.RestErrorDto;
+import org.springframework.samples.petclinic.rest.dto.UserDto;
+import io.swagger.v3.oas.annotations.Operation;
+import io.swagger.v3.oas.annotations.Parameter;
+import io.swagger.v3.oas.annotations.Parameters;
+import io.swagger.v3.oas.annotations.media.Content;
+import io.swagger.v3.oas.annotations.media.Schema;
+import io.swagger.v3.oas.annotations.responses.ApiResponse;
+import io.swagger.v3.oas.annotations.security.SecurityRequirement;
+import io.swagger.v3.oas.annotations.tags.Tag;
+import org.springframework.http.HttpStatus;
+import org.springframework.http.MediaType;
+import org.springframework.http.ResponseEntity;
+import org.springframework.validation.annotation.Validated;
+import org.springframework.web.bind.annotation.*;
+import org.springframework.web.context.request.NativeWebRequest;
+import org.springframework.web.multipart.MultipartFile;
+
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import javax.annotation.Generated;
+
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+@Validated
+@Tag(name = "users", description = "Endpoints related to users.")
+public interface UsersApi {
+
+    default Optional<NativeWebRequest> getRequest() {
+        return Optional.empty();
+    }
+
+    /**
+     * POST /users : Create a user
+     * Creates a user.
+     *
+     * @param userDto The user (required)
+     * @return User created successfully. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or User not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "addUser",
+        summary = "Create a user",
+        tags = { "user" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "User created successfully.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = UserDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "User not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.POST,
+        value = "/users",
+        produces = { "application/json" },
+        consumes = { "application/json" }
+    )
+    default ResponseEntity<UserDto> addUser(
+        @Parameter(name = "UserDto", description = "The user", required = true) @Valid @RequestBody UserDto userDto
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "{ \"password\" : \"1234\", \"roles\" : [ { \"name\" : \"admin\" }, { \"name\" : \"admin\" } ], \"enabled\" : true, \"username\" : \"john.doe\" }";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+}

--- a/VetsApi.java
+++ b/VetsApi.java
@@ -0,0 +1,301 @@
+/**
+ * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.0.1).
+ * https://openapi-generator.tech
+ * Do not edit the class manually.
+ */
+package org.springframework.samples.petclinic.rest.api;
+
+import org.springframework.samples.petclinic.rest.dto.RestErrorDto;
+import org.springframework.samples.petclinic.rest.dto.VetDto;
+import io.swagger.v3.oas.annotations.Operation;
+import io.swagger.v3.oas.annotations.Parameter;
+import io.swagger.v3.oas.annotations.Parameters;
+import io.swagger.v3.oas.annotations.media.Content;
+import io.swagger.v3.oas.annotations.media.Schema;
+import io.swagger.v3.oas.annotations.responses.ApiResponse;
+import io.swagger.v3.oas.annotations.security.SecurityRequirement;
+import io.swagger.v3.oas.annotations.tags.Tag;
+import org.springframework.http.HttpStatus;
+import org.springframework.http.MediaType;
+import org.springframework.http.ResponseEntity;
+import org.springframework.validation.annotation.Validated;
+import org.springframework.web.bind.annotation.*;
+import org.springframework.web.context.request.NativeWebRequest;
+import org.springframework.web.multipart.MultipartFile;
+
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import javax.annotation.Generated;
+
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+@Validated
+@Tag(name = "vets", description = "Endpoints related to vets.")
+public interface VetsApi {
+
+    default Optional<NativeWebRequest> getRequest() {
+        return Optional.empty();
+    }
+
+    /**
+     * POST /vets : Create a Vet
+     * Creates a vet .
+     *
+     * @param vetDto The vet (required)
+     * @return Vet created successfully. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Vet not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "addVet",
+        summary = "Create a Vet",
+        tags = { "vet" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Vet created successfully.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = VetDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Vet not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.POST,
+        value = "/vets",
+        produces = { "application/json" },
+        consumes = { "application/json" }
+    )
+    default ResponseEntity<VetDto> addVet(
+        @Parameter(name = "VetDto", description = "The vet", required = true) @Valid @RequestBody VetDto vetDto
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * DELETE /vets/{vetId} : Delete a vet by ID
+     * Returns the vet or a 404 error.
+     *
+     * @param vetId The ID of the vet. (required)
+     * @return Vet details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Vet not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "deleteVet",
+        summary = "Delete a vet by ID",
+        tags = { "vets" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Vet details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = VetDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Vet not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.DELETE,
+        value = "/vets/{vetId}",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<VetDto> deleteVet(
+        @Min(0) @Parameter(name = "vetId", description = "The ID of the vet.", required = true) @PathVariable("vetId") Integer vetId
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * GET /vets/{vetId} : Get a vet by ID
+     * Returns the vet or a 404 error.
+     *
+     * @param vetId The ID of the vet. (required)
+     * @return Vet details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Vet not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "getVet",
+        summary = "Get a vet by ID",
+        tags = { "vet" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Vet details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = VetDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Vet not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.GET,
+        value = "/vets/{vetId}",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<VetDto> getVet(
+        @Min(0) @Parameter(name = "vetId", description = "The ID of the vet.", required = true) @PathVariable("vetId") Integer vetId
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * GET /vets : Lists vets
+     * Returns an array of vets.
+     *
+     * @return Vets found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "listVets",
+        summary = "Lists vets",
+        tags = { "vet" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Vets found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = VetDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.GET,
+        value = "/vets",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<List<VetDto>> listVets(
+        
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * PUT /vets/{vetId} : Update a vet  by ID
+     * Returns the vet or a 404 error.
+     *
+     * @param vetId The ID of the vet. (required)
+     * @param vetDto The vet (required)
+     * @return Pet type details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Vet not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "updateVet",
+        summary = "Update a vet  by ID",
+        tags = { "vet" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Pet type details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = VetDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Vet not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.PUT,
+        value = "/vets/{vetId}",
+        produces = { "application/json" },
+        consumes = { "application/json" }
+    )
+    default ResponseEntity<VetDto> updateVet(
+        @Min(0) @Parameter(name = "vetId", description = "The ID of the vet.", required = true) @PathVariable("vetId") Integer vetId,
+        @Parameter(name = "VetDto", description = "The vet", required = true) @Valid @RequestBody VetDto vetDto
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+}

--- a/VisitsApi.java
+++ b/VisitsApi.java
@@ -0,0 +1,301 @@
+/**
+ * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.0.1).
+ * https://openapi-generator.tech
+ * Do not edit the class manually.
+ */
+package org.springframework.samples.petclinic.rest.api;
+
+import org.springframework.samples.petclinic.rest.dto.RestErrorDto;
+import org.springframework.samples.petclinic.rest.dto.VisitDto;
+import io.swagger.v3.oas.annotations.Operation;
+import io.swagger.v3.oas.annotations.Parameter;
+import io.swagger.v3.oas.annotations.Parameters;
+import io.swagger.v3.oas.annotations.media.Content;
+import io.swagger.v3.oas.annotations.media.Schema;
+import io.swagger.v3.oas.annotations.responses.ApiResponse;
+import io.swagger.v3.oas.annotations.security.SecurityRequirement;
+import io.swagger.v3.oas.annotations.tags.Tag;
+import org.springframework.http.HttpStatus;
+import org.springframework.http.MediaType;
+import org.springframework.http.ResponseEntity;
+import org.springframework.validation.annotation.Validated;
+import org.springframework.web.bind.annotation.*;
+import org.springframework.web.context.request.NativeWebRequest;
+import org.springframework.web.multipart.MultipartFile;
+
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import javax.annotation.Generated;
+
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+@Validated
+@Tag(name = "visits", description = "Endpoints related to vet visits.")
+public interface VisitsApi {
+
+    default Optional<NativeWebRequest> getRequest() {
+        return Optional.empty();
+    }
+
+    /**
+     * POST /visits : Create a visit
+     * Creates a visit.
+     *
+     * @param visitDto The visit (required)
+     * @return visit created successfully. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Visit not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "addVisit",
+        summary = "Create a visit",
+        tags = { "visit" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "visit created successfully.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = VisitDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Visit not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.POST,
+        value = "/visits",
+        produces = { "application/json" },
+        consumes = { "application/json" }
+    )
+    default ResponseEntity<VisitDto> addVisit(
+        @Parameter(name = "VisitDto", description = "The visit", required = true) @Valid @RequestBody VisitDto visitDto
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * DELETE /visits/{visitId} : Delete a visit by ID
+     * Returns the visit or a 404 error.
+     *
+     * @param visitId The ID of the visit. (required)
+     * @return Visit details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Visit not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "deleteVisit",
+        summary = "Delete a visit by ID",
+        tags = { "visit" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Visit details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = VisitDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Visit not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.DELETE,
+        value = "/visits/{visitId}",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<VisitDto> deleteVisit(
+        @Min(0) @Parameter(name = "visitId", description = "The ID of the visit.", required = true) @PathVariable("visitId") Integer visitId
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * GET /visits/{visitId} : Get a visit by ID
+     * Returns the visit or a 404 error.
+     *
+     * @param visitId The ID of the visit. (required)
+     * @return Visit details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Visit not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "getVisit",
+        summary = "Get a visit by ID",
+        tags = { "visit" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Visit details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = VisitDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Visit not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.GET,
+        value = "/visits/{visitId}",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<VisitDto> getVisit(
+        @Min(0) @Parameter(name = "visitId", description = "The ID of the visit.", required = true) @PathVariable("visitId") Integer visitId
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * GET /visits : Lists visits
+     * Returns an array of visit .
+     *
+     * @return visits found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "listVisits",
+        summary = "Lists visits",
+        tags = { "visit" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "visits found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = VisitDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.GET,
+        value = "/visits",
+        produces = { "application/json" }
+    )
+    default ResponseEntity<List<VisitDto>> listVisits(
+        
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+
+    /**
+     * PUT /visits/{visitId} : Update a visit by ID
+     * Returns the visit or a 404 error.
+     *
+     * @param visitId The ID of the visit. (required)
+     * @param visitDto The visit (required)
+     * @return Visit details found and returned. (status code 200)
+     *         or Not modified. (status code 304)
+     *         or Bad request. (status code 400)
+     *         or Visit not found. (status code 404)
+     *         or Server error. (status code 500)
+     */
+    @Operation(
+        operationId = "updateVisit",
+        summary = "Update a visit by ID",
+        tags = { "visit" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Visit details found and returned.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = VisitDto.class))
+            }),
+            @ApiResponse(responseCode = "304", description = "Not modified."),
+            @ApiResponse(responseCode = "400", description = "Bad request.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "404", description = "Visit not found.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            }),
+            @ApiResponse(responseCode = "500", description = "Server error.", content = {
+                @Content(mediaType = "application/json", schema = @Schema(implementation = RestErrorDto.class))
+            })
+        }
+    )
+    @RequestMapping(
+        method = RequestMethod.PUT,
+        value = "/visits/{visitId}",
+        produces = { "application/json" },
+        consumes = { "application/json" }
+    )
+    default ResponseEntity<VisitDto> updateVisit(
+        @Min(0) @Parameter(name = "visitId", description = "The ID of the visit.", required = true) @PathVariable("visitId") Integer visitId,
+        @Parameter(name = "VisitDto", description = "The visit", required = true) @Valid @RequestBody VisitDto visitDto
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "null";
+                    ApiUtil.setExampleResponse(request, "application/json", exampleString);
+                    break;
+                }
+            }
+        });
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+}

--- a/OwnerAllOfDto.java
+++ b/OwnerAllOfDto.java
@@ -0,0 +1,122 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.util.ArrayList;
+import java.util.List;
+import org.springframework.samples.petclinic.rest.dto.PetDto;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * OwnerAllOfDto
+ */
+
+@JsonTypeName("Owner_allOf")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class OwnerAllOfDto {
+
+  @JsonProperty("id")
+  private Integer id;
+
+  @JsonProperty("pets")
+  @Valid
+  private List<PetDto> pets = new ArrayList<>();
+
+  public OwnerAllOfDto id(Integer id) {
+    this.id = id;
+    return this;
+  }
+
+  /**
+   * The ID of the pet owner.
+   * minimum: 0
+   * @return id
+  */
+  @Min(0) 
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet owner.", required = false)
+  public Integer getId() {
+    return id;
+  }
+
+  public void setId(Integer id) {
+    this.id = id;
+  }
+
+  public OwnerAllOfDto pets(List<PetDto> pets) {
+    this.pets = pets;
+    return this;
+  }
+
+  public OwnerAllOfDto addPetsItem(PetDto petsItem) {
+    if (this.pets == null) {
+      this.pets = new ArrayList<>();
+    }
+    this.pets.add(petsItem);
+    return this;
+  }
+
+  /**
+   * The pets owned by this individual including any booked vet visits.
+   * @return pets
+  */
+  @Valid 
+  @Schema(name = "pets", accessMode = Schema.AccessMode.READ_ONLY, description = "The pets owned by this individual including any booked vet visits.", required = true)
+  public List<PetDto> getPets() {
+    return pets;
+  }
+
+  public void setPets(List<PetDto> pets) {
+    this.pets = pets;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    OwnerAllOfDto ownerAllOf = (OwnerAllOfDto) o;
+    return Objects.equals(this.id, ownerAllOf.id) &&
+        Objects.equals(this.pets, ownerAllOf.pets);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(id, pets);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class OwnerAllOfDto {\n");
+    sb.append("    id: ").append(toIndentedString(id)).append("\n");
+    sb.append("    pets: ").append(toIndentedString(pets)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/OwnerDto.java
+++ b/OwnerDto.java
@@ -0,0 +1,245 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.util.ArrayList;
+import java.util.List;
+import org.springframework.samples.petclinic.rest.dto.OwnerAllOfDto;
+import org.springframework.samples.petclinic.rest.dto.OwnerFieldsDto;
+import org.springframework.samples.petclinic.rest.dto.PetDto;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * A pet owner.
+ */
+
+@Schema(name = "Owner", description = "A pet owner.")
+@JsonTypeName("Owner")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class OwnerDto {
+
+  @JsonProperty("firstName")
+  private String firstName;
+
+  @JsonProperty("lastName")
+  private String lastName;
+
+  @JsonProperty("address")
+  private String address;
+
+  @JsonProperty("city")
+  private String city;
+
+  @JsonProperty("telephone")
+  private String telephone;
+
+  @JsonProperty("id")
+  private Integer id;
+
+  @JsonProperty("pets")
+  @Valid
+  private List<PetDto> pets = new ArrayList<>();
+
+  public OwnerDto firstName(String firstName) {
+    this.firstName = firstName;
+    return this;
+  }
+
+  /**
+   * The first name of the pet owner.
+   * @return firstName
+  */
+  @NotNull @Pattern(regexp = "^[a-zA-Z]*$") @Size(min = 1, max = 30) 
+  @Schema(name = "firstName", example = "George", description = "The first name of the pet owner.", required = true)
+  public String getFirstName() {
+    return firstName;
+  }
+
+  public void setFirstName(String firstName) {
+    this.firstName = firstName;
+  }
+
+  public OwnerDto lastName(String lastName) {
+    this.lastName = lastName;
+    return this;
+  }
+
+  /**
+   * The last name of the pet owner.
+   * @return lastName
+  */
+  @NotNull @Pattern(regexp = "^[a-zA-Z]*$") @Size(min = 1, max = 30) 
+  @Schema(name = "lastName", example = "Franklin", description = "The last name of the pet owner.", required = true)
+  public String getLastName() {
+    return lastName;
+  }
+
+  public void setLastName(String lastName) {
+    this.lastName = lastName;
+  }
+
+  public OwnerDto address(String address) {
+    this.address = address;
+    return this;
+  }
+
+  /**
+   * The postal address of the pet owner.
+   * @return address
+  */
+  @NotNull @Size(min = 1, max = 255) 
+  @Schema(name = "address", example = "110 W. Liberty St.", description = "The postal address of the pet owner.", required = true)
+  public String getAddress() {
+    return address;
+  }
+
+  public void setAddress(String address) {
+    this.address = address;
+  }
+
+  public OwnerDto city(String city) {
+    this.city = city;
+    return this;
+  }
+
+  /**
+   * The city of the pet owner.
+   * @return city
+  */
+  @NotNull @Size(min = 1, max = 80) 
+  @Schema(name = "city", example = "Madison", description = "The city of the pet owner.", required = true)
+  public String getCity() {
+    return city;
+  }
+
+  public void setCity(String city) {
+    this.city = city;
+  }
+
+  public OwnerDto telephone(String telephone) {
+    this.telephone = telephone;
+    return this;
+  }
+
+  /**
+   * The telephone number of the pet owner.
+   * @return telephone
+  */
+  @NotNull @Pattern(regexp = "^[0-9]*$") @Size(min = 1, max = 20) 
+  @Schema(name = "telephone", example = "6085551023", description = "The telephone number of the pet owner.", required = true)
+  public String getTelephone() {
+    return telephone;
+  }
+
+  public void setTelephone(String telephone) {
+    this.telephone = telephone;
+  }
+
+  public OwnerDto id(Integer id) {
+    this.id = id;
+    return this;
+  }
+
+  /**
+   * The ID of the pet owner.
+   * minimum: 0
+   * @return id
+  */
+  @Min(0) 
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet owner.", required = false)
+  public Integer getId() {
+    return id;
+  }
+
+  public void setId(Integer id) {
+    this.id = id;
+  }
+
+  public OwnerDto pets(List<PetDto> pets) {
+    this.pets = pets;
+    return this;
+  }
+
+  public OwnerDto addPetsItem(PetDto petsItem) {
+    if (this.pets == null) {
+      this.pets = new ArrayList<>();
+    }
+    this.pets.add(petsItem);
+    return this;
+  }
+
+  /**
+   * The pets owned by this individual including any booked vet visits.
+   * @return pets
+  */
+  @Valid 
+  @Schema(name = "pets", accessMode = Schema.AccessMode.READ_ONLY, description = "The pets owned by this individual including any booked vet visits.", required = true)
+  public List<PetDto> getPets() {
+    return pets;
+  }
+
+  public void setPets(List<PetDto> pets) {
+    this.pets = pets;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    OwnerDto owner = (OwnerDto) o;
+    return Objects.equals(this.firstName, owner.firstName) &&
+        Objects.equals(this.lastName, owner.lastName) &&
+        Objects.equals(this.address, owner.address) &&
+        Objects.equals(this.city, owner.city) &&
+        Objects.equals(this.telephone, owner.telephone) &&
+        Objects.equals(this.id, owner.id) &&
+        Objects.equals(this.pets, owner.pets);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(firstName, lastName, address, city, telephone, id, pets);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class OwnerDto {\n");
+    sb.append("    firstName: ").append(toIndentedString(firstName)).append("\n");
+    sb.append("    lastName: ").append(toIndentedString(lastName)).append("\n");
+    sb.append("    address: ").append(toIndentedString(address)).append("\n");
+    sb.append("    city: ").append(toIndentedString(city)).append("\n");
+    sb.append("    telephone: ").append(toIndentedString(telephone)).append("\n");
+    sb.append("    id: ").append(toIndentedString(id)).append("\n");
+    sb.append("    pets: ").append(toIndentedString(pets)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/OwnerFieldsDto.java
+++ b/OwnerFieldsDto.java
@@ -0,0 +1,182 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * Editable fields of a pet owner.
+ */
+
+@Schema(name = "OwnerFields", description = "Editable fields of a pet owner.")
+@JsonTypeName("OwnerFields")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class OwnerFieldsDto {
+
+  @JsonProperty("firstName")
+  private String firstName;
+
+  @JsonProperty("lastName")
+  private String lastName;
+
+  @JsonProperty("address")
+  private String address;
+
+  @JsonProperty("city")
+  private String city;
+
+  @JsonProperty("telephone")
+  private String telephone;
+
+  public OwnerFieldsDto firstName(String firstName) {
+    this.firstName = firstName;
+    return this;
+  }
+
+  /**
+   * The first name of the pet owner.
+   * @return firstName
+  */
+  @NotNull @Pattern(regexp = "^[a-zA-Z]*$") @Size(min = 1, max = 30) 
+  @Schema(name = "firstName", example = "George", description = "The first name of the pet owner.", required = true)
+  public String getFirstName() {
+    return firstName;
+  }
+
+  public void setFirstName(String firstName) {
+    this.firstName = firstName;
+  }
+
+  public OwnerFieldsDto lastName(String lastName) {
+    this.lastName = lastName;
+    return this;
+  }
+
+  /**
+   * The last name of the pet owner.
+   * @return lastName
+  */
+  @NotNull @Pattern(regexp = "^[a-zA-Z]*$") @Size(min = 1, max = 30) 
+  @Schema(name = "lastName", example = "Franklin", description = "The last name of the pet owner.", required = true)
+  public String getLastName() {
+    return lastName;
+  }
+
+  public void setLastName(String lastName) {
+    this.lastName = lastName;
+  }
+
+  public OwnerFieldsDto address(String address) {
+    this.address = address;
+    return this;
+  }
+
+  /**
+   * The postal address of the pet owner.
+   * @return address
+  */
+  @NotNull @Size(min = 1, max = 255) 
+  @Schema(name = "address", example = "110 W. Liberty St.", description = "The postal address of the pet owner.", required = true)
+  public String getAddress() {
+    return address;
+  }
+
+  public void setAddress(String address) {
+    this.address = address;
+  }
+
+  public OwnerFieldsDto city(String city) {
+    this.city = city;
+    return this;
+  }
+
+  /**
+   * The city of the pet owner.
+   * @return city
+  */
+  @NotNull @Size(min = 1, max = 80) 
+  @Schema(name = "city", example = "Madison", description = "The city of the pet owner.", required = true)
+  public String getCity() {
+    return city;
+  }
+
+  public void setCity(String city) {
+    this.city = city;
+  }
+
+  public OwnerFieldsDto telephone(String telephone) {
+    this.telephone = telephone;
+    return this;
+  }
+
+  /**
+   * The telephone number of the pet owner.
+   * @return telephone
+  */
+  @NotNull @Pattern(regexp = "^[0-9]*$") @Size(min = 1, max = 20) 
+  @Schema(name = "telephone", example = "6085551023", description = "The telephone number of the pet owner.", required = true)
+  public String getTelephone() {
+    return telephone;
+  }
+
+  public void setTelephone(String telephone) {
+    this.telephone = telephone;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    OwnerFieldsDto ownerFields = (OwnerFieldsDto) o;
+    return Objects.equals(this.firstName, ownerFields.firstName) &&
+        Objects.equals(this.lastName, ownerFields.lastName) &&
+        Objects.equals(this.address, ownerFields.address) &&
+        Objects.equals(this.city, ownerFields.city) &&
+        Objects.equals(this.telephone, ownerFields.telephone);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(firstName, lastName, address, city, telephone);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class OwnerFieldsDto {\n");
+    sb.append("    firstName: ").append(toIndentedString(firstName)).append("\n");
+    sb.append("    lastName: ").append(toIndentedString(lastName)).append("\n");
+    sb.append("    address: ").append(toIndentedString(address)).append("\n");
+    sb.append("    city: ").append(toIndentedString(city)).append("\n");
+    sb.append("    telephone: ").append(toIndentedString(telephone)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/PetAllOfDto.java
+++ b/PetAllOfDto.java
@@ -0,0 +1,147 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.util.ArrayList;
+import java.util.List;
+import org.springframework.samples.petclinic.rest.dto.VisitDto;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * PetAllOfDto
+ */
+
+@JsonTypeName("Pet_allOf")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class PetAllOfDto {
+
+  @JsonProperty("id")
+  private Integer id;
+
+  @JsonProperty("ownerId")
+  private Integer ownerId;
+
+  @JsonProperty("visits")
+  @Valid
+  private List<VisitDto> visits = new ArrayList<>();
+
+  public PetAllOfDto id(Integer id) {
+    this.id = id;
+    return this;
+  }
+
+  /**
+   * The ID of the pet.
+   * minimum: 0
+   * @return id
+  */
+  @Min(0) 
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet.", required = true)
+  public Integer getId() {
+    return id;
+  }
+
+  public void setId(Integer id) {
+    this.id = id;
+  }
+
+  public PetAllOfDto ownerId(Integer ownerId) {
+    this.ownerId = ownerId;
+    return this;
+  }
+
+  /**
+   * The ID of the pet's owner.
+   * minimum: 0
+   * @return ownerId
+  */
+  @Min(0) 
+  @Schema(name = "ownerId", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet's owner.", required = false)
+  public Integer getOwnerId() {
+    return ownerId;
+  }
+
+  public void setOwnerId(Integer ownerId) {
+    this.ownerId = ownerId;
+  }
+
+  public PetAllOfDto visits(List<VisitDto> visits) {
+    this.visits = visits;
+    return this;
+  }
+
+  public PetAllOfDto addVisitsItem(VisitDto visitsItem) {
+    if (this.visits == null) {
+      this.visits = new ArrayList<>();
+    }
+    this.visits.add(visitsItem);
+    return this;
+  }
+
+  /**
+   * Vet visit bookings for this pet.
+   * @return visits
+  */
+  @Valid 
+  @Schema(name = "visits", accessMode = Schema.AccessMode.READ_ONLY, description = "Vet visit bookings for this pet.", required = true)
+  public List<VisitDto> getVisits() {
+    return visits;
+  }
+
+  public void setVisits(List<VisitDto> visits) {
+    this.visits = visits;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    PetAllOfDto petAllOf = (PetAllOfDto) o;
+    return Objects.equals(this.id, petAllOf.id) &&
+        Objects.equals(this.ownerId, petAllOf.ownerId) &&
+        Objects.equals(this.visits, petAllOf.visits);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(id, ownerId, visits);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class PetAllOfDto {\n");
+    sb.append("    id: ").append(toIndentedString(id)).append("\n");
+    sb.append("    ownerId: ").append(toIndentedString(ownerId)).append("\n");
+    sb.append("    visits: ").append(toIndentedString(visits)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/PetDto.java
+++ b/PetDto.java
@@ -0,0 +1,226 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.LocalDate;
+import java.util.ArrayList;
+import java.util.List;
+import org.springframework.format.annotation.DateTimeFormat;
+import org.springframework.samples.petclinic.rest.dto.PetAllOfDto;
+import org.springframework.samples.petclinic.rest.dto.PetFieldsDto;
+import org.springframework.samples.petclinic.rest.dto.PetTypeDto;
+import org.springframework.samples.petclinic.rest.dto.VisitDto;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * A pet.
+ */
+
+@Schema(name = "Pet", description = "A pet.")
+@JsonTypeName("Pet")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class PetDto {
+
+  @JsonProperty("name")
+  private String name;
+
+  @JsonProperty("birthDate")
+  @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
+  private LocalDate birthDate;
+
+  @JsonProperty("type")
+  private PetTypeDto type;
+
+  @JsonProperty("id")
+  private Integer id;
+
+  @JsonProperty("ownerId")
+  private Integer ownerId;
+
+  @JsonProperty("visits")
+  @Valid
+  private List<VisitDto> visits = new ArrayList<>();
+
+  public PetDto name(String name) {
+    this.name = name;
+    return this;
+  }
+
+  /**
+   * The name of the pet.
+   * @return name
+  */
+  @NotNull @Size(max = 30) 
+  @Schema(name = "name", example = "Leo", description = "The name of the pet.", required = true)
+  public String getName() {
+    return name;
+  }
+
+  public void setName(String name) {
+    this.name = name;
+  }
+
+  public PetDto birthDate(LocalDate birthDate) {
+    this.birthDate = birthDate;
+    return this;
+  }
+
+  /**
+   * The date of birth of the pet.
+   * @return birthDate
+  */
+  @NotNull @Valid 
+  @Schema(name = "birthDate", example = "Tue Sep 07 05:30:00 IST 2010", description = "The date of birth of the pet.", required = true)
+  public LocalDate getBirthDate() {
+    return birthDate;
+  }
+
+  public void setBirthDate(LocalDate birthDate) {
+    this.birthDate = birthDate;
+  }
+
+  public PetDto type(PetTypeDto type) {
+    this.type = type;
+    return this;
+  }
+
+  /**
+   * Get type
+   * @return type
+  */
+  @NotNull @Valid 
+  @Schema(name = "type", required = true)
+  public PetTypeDto getType() {
+    return type;
+  }
+
+  public void setType(PetTypeDto type) {
+    this.type = type;
+  }
+
+  public PetDto id(Integer id) {
+    this.id = id;
+    return this;
+  }
+
+  /**
+   * The ID of the pet.
+   * minimum: 0
+   * @return id
+  */
+  @Min(0) 
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet.", required = true)
+  public Integer getId() {
+    return id;
+  }
+
+  public void setId(Integer id) {
+    this.id = id;
+  }
+
+  public PetDto ownerId(Integer ownerId) {
+    this.ownerId = ownerId;
+    return this;
+  }
+
+  /**
+   * The ID of the pet's owner.
+   * minimum: 0
+   * @return ownerId
+  */
+  @Min(0) 
+  @Schema(name = "ownerId", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet's owner.", required = false)
+  public Integer getOwnerId() {
+    return ownerId;
+  }
+
+  public void setOwnerId(Integer ownerId) {
+    this.ownerId = ownerId;
+  }
+
+  public PetDto visits(List<VisitDto> visits) {
+    this.visits = visits;
+    return this;
+  }
+
+  public PetDto addVisitsItem(VisitDto visitsItem) {
+    if (this.visits == null) {
+      this.visits = new ArrayList<>();
+    }
+    this.visits.add(visitsItem);
+    return this;
+  }
+
+  /**
+   * Vet visit bookings for this pet.
+   * @return visits
+  */
+  @Valid 
+  @Schema(name = "visits", accessMode = Schema.AccessMode.READ_ONLY, description = "Vet visit bookings for this pet.", required = true)
+  public List<VisitDto> getVisits() {
+    return visits;
+  }
+
+  public void setVisits(List<VisitDto> visits) {
+    this.visits = visits;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    PetDto pet = (PetDto) o;
+    return Objects.equals(this.name, pet.name) &&
+        Objects.equals(this.birthDate, pet.birthDate) &&
+        Objects.equals(this.type, pet.type) &&
+        Objects.equals(this.id, pet.id) &&
+        Objects.equals(this.ownerId, pet.ownerId) &&
+        Objects.equals(this.visits, pet.visits);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(name, birthDate, type, id, ownerId, visits);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class PetDto {\n");
+    sb.append("    name: ").append(toIndentedString(name)).append("\n");
+    sb.append("    birthDate: ").append(toIndentedString(birthDate)).append("\n");
+    sb.append("    type: ").append(toIndentedString(type)).append("\n");
+    sb.append("    id: ").append(toIndentedString(id)).append("\n");
+    sb.append("    ownerId: ").append(toIndentedString(ownerId)).append("\n");
+    sb.append("    visits: ").append(toIndentedString(visits)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/PetFieldsDto.java
+++ b/PetFieldsDto.java
@@ -0,0 +1,138 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.LocalDate;
+import org.springframework.format.annotation.DateTimeFormat;
+import org.springframework.samples.petclinic.rest.dto.PetTypeDto;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * Editable fields of a pet.
+ */
+
+@Schema(name = "PetFields", description = "Editable fields of a pet.")
+@JsonTypeName("PetFields")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class PetFieldsDto {
+
+  @JsonProperty("name")
+  private String name;
+
+  @JsonProperty("birthDate")
+  @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
+  private LocalDate birthDate;
+
+  @JsonProperty("type")
+  private PetTypeDto type;
+
+  public PetFieldsDto name(String name) {
+    this.name = name;
+    return this;
+  }
+
+  /**
+   * The name of the pet.
+   * @return name
+  */
+  @NotNull @Size(max = 30) 
+  @Schema(name = "name", example = "Leo", description = "The name of the pet.", required = true)
+  public String getName() {
+    return name;
+  }
+
+  public void setName(String name) {
+    this.name = name;
+  }
+
+  public PetFieldsDto birthDate(LocalDate birthDate) {
+    this.birthDate = birthDate;
+    return this;
+  }
+
+  /**
+   * The date of birth of the pet.
+   * @return birthDate
+  */
+  @NotNull @Valid 
+  @Schema(name = "birthDate", example = "Tue Sep 07 05:30:00 IST 2010", description = "The date of birth of the pet.", required = true)
+  public LocalDate getBirthDate() {
+    return birthDate;
+  }
+
+  public void setBirthDate(LocalDate birthDate) {
+    this.birthDate = birthDate;
+  }
+
+  public PetFieldsDto type(PetTypeDto type) {
+    this.type = type;
+    return this;
+  }
+
+  /**
+   * Get type
+   * @return type
+  */
+  @NotNull @Valid 
+  @Schema(name = "type", required = true)
+  public PetTypeDto getType() {
+    return type;
+  }
+
+  public void setType(PetTypeDto type) {
+    this.type = type;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    PetFieldsDto petFields = (PetFieldsDto) o;
+    return Objects.equals(this.name, petFields.name) &&
+        Objects.equals(this.birthDate, petFields.birthDate) &&
+        Objects.equals(this.type, petFields.type);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(name, birthDate, type);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class PetFieldsDto {\n");
+    sb.append("    name: ").append(toIndentedString(name)).append("\n");
+    sb.append("    birthDate: ").append(toIndentedString(birthDate)).append("\n");
+    sb.append("    type: ").append(toIndentedString(type)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/PetTypeAllOfDto.java
+++ b/PetTypeAllOfDto.java
@@ -0,0 +1,86 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * PetTypeAllOfDto
+ */
+
+@JsonTypeName("PetType_allOf")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class PetTypeAllOfDto {
+
+  @JsonProperty("id")
+  private Integer id;
+
+  public PetTypeAllOfDto id(Integer id) {
+    this.id = id;
+    return this;
+  }
+
+  /**
+   * The ID of the pet type.
+   * minimum: 0
+   * @return id
+  */
+  @Min(0) 
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet type.", required = true)
+  public Integer getId() {
+    return id;
+  }
+
+  public void setId(Integer id) {
+    this.id = id;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    PetTypeAllOfDto petTypeAllOf = (PetTypeAllOfDto) o;
+    return Objects.equals(this.id, petTypeAllOf.id);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(id);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class PetTypeAllOfDto {\n");
+    sb.append("    id: ").append(toIndentedString(id)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/PetTypeDto.java
+++ b/PetTypeDto.java
@@ -0,0 +1,113 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import org.springframework.samples.petclinic.rest.dto.PetTypeAllOfDto;
+import org.springframework.samples.petclinic.rest.dto.PetTypeFieldsDto;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * A pet type.
+ */
+
+@Schema(name = "PetType", description = "A pet type.")
+@JsonTypeName("PetType")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class PetTypeDto {
+
+  @JsonProperty("name")
+  private String name;
+
+  @JsonProperty("id")
+  private Integer id;
+
+  public PetTypeDto name(String name) {
+    this.name = name;
+    return this;
+  }
+
+  /**
+   * The name of the pet type.
+   * @return name
+  */
+  @NotNull @Size(min = 1, max = 80) 
+  @Schema(name = "name", example = "cat", description = "The name of the pet type.", required = true)
+  public String getName() {
+    return name;
+  }
+
+  public void setName(String name) {
+    this.name = name;
+  }
+
+  public PetTypeDto id(Integer id) {
+    this.id = id;
+    return this;
+  }
+
+  /**
+   * The ID of the pet type.
+   * minimum: 0
+   * @return id
+  */
+  @Min(0) 
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet type.", required = true)
+  public Integer getId() {
+    return id;
+  }
+
+  public void setId(Integer id) {
+    this.id = id;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    PetTypeDto petType = (PetTypeDto) o;
+    return Objects.equals(this.name, petType.name) &&
+        Objects.equals(this.id, petType.id);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(name, id);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class PetTypeDto {\n");
+    sb.append("    name: ").append(toIndentedString(name)).append("\n");
+    sb.append("    id: ").append(toIndentedString(id)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/PetTypeFieldsDto.java
+++ b/PetTypeFieldsDto.java
@@ -0,0 +1,86 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * Editable fields of a pet type.
+ */
+
+@Schema(name = "PetTypeFields", description = "Editable fields of a pet type.")
+@JsonTypeName("PetTypeFields")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class PetTypeFieldsDto {
+
+  @JsonProperty("name")
+  private String name;
+
+  public PetTypeFieldsDto name(String name) {
+    this.name = name;
+    return this;
+  }
+
+  /**
+   * The name of the pet type.
+   * @return name
+  */
+  @NotNull @Size(min = 1, max = 80) 
+  @Schema(name = "name", example = "cat", description = "The name of the pet type.", required = true)
+  public String getName() {
+    return name;
+  }
+
+  public void setName(String name) {
+    this.name = name;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    PetTypeFieldsDto petTypeFields = (PetTypeFieldsDto) o;
+    return Objects.equals(this.name, petTypeFields.name);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(name);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class PetTypeFieldsDto {\n");
+    sb.append("    name: ").append(toIndentedString(name)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/RestErrorDto.java
+++ b/RestErrorDto.java
@@ -0,0 +1,246 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.net.URI;
+import java.time.OffsetDateTime;
+import java.util.ArrayList;
+import java.util.List;
+import org.springframework.format.annotation.DateTimeFormat;
+import org.springframework.samples.petclinic.rest.dto.ValidationMessageDto;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * The schema for all error responses.
+ */
+
+@Schema(name = "RestError", description = "The schema for all error responses.")
+@JsonTypeName("RestError")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class RestErrorDto {
+
+  @JsonProperty("status")
+  private Integer status;
+
+  @JsonProperty("error")
+  private String error;
+
+  @JsonProperty("path")
+  private URI path;
+
+  @JsonProperty("timestamp")
+  @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME)
+  private OffsetDateTime timestamp;
+
+  @JsonProperty("message")
+  private String message;
+
+  @JsonProperty("schemaValidationErrors")
+  @Valid
+  private List<ValidationMessageDto> schemaValidationErrors = new ArrayList<>();
+
+  @JsonProperty("trace")
+  private String trace;
+
+  public RestErrorDto status(Integer status) {
+    this.status = status;
+    return this;
+  }
+
+  /**
+   * The HTTP status code.
+   * @return status
+  */
+  
+  @Schema(name = "status", accessMode = Schema.AccessMode.READ_ONLY, example = "400", description = "The HTTP status code.", required = true)
+  public Integer getStatus() {
+    return status;
+  }
+
+  public void setStatus(Integer status) {
+    this.status = status;
+  }
+
+  public RestErrorDto error(String error) {
+    this.error = error;
+    return this;
+  }
+
+  /**
+   * The short error message.
+   * @return error
+  */
+  
+  @Schema(name = "error", accessMode = Schema.AccessMode.READ_ONLY, example = "Bad Request", description = "The short error message.", required = true)
+  public String getError() {
+    return error;
+  }
+
+  public void setError(String error) {
+    this.error = error;
+  }
+
+  public RestErrorDto path(URI path) {
+    this.path = path;
+    return this;
+  }
+
+  /**
+   * The path of the URL for this request.
+   * @return path
+  */
+  @Valid 
+  @Schema(name = "path", accessMode = Schema.AccessMode.READ_ONLY, example = "/api/owners", description = "The path of the URL for this request.", required = true)
+  public URI getPath() {
+    return path;
+  }
+
+  public void setPath(URI path) {
+    this.path = path;
+  }
+
+  public RestErrorDto timestamp(OffsetDateTime timestamp) {
+    this.timestamp = timestamp;
+    return this;
+  }
+
+  /**
+   * The time the error occured.
+   * @return timestamp
+  */
+  @Valid 
+  @Schema(name = "timestamp", accessMode = Schema.AccessMode.READ_ONLY, description = "The time the error occured.", required = true)
+  public OffsetDateTime getTimestamp() {
+    return timestamp;
+  }
+
+  public void setTimestamp(OffsetDateTime timestamp) {
+    this.timestamp = timestamp;
+  }
+
+  public RestErrorDto message(String message) {
+    this.message = message;
+    return this;
+  }
+
+  /**
+   * The long error message.
+   * @return message
+  */
+  
+  @Schema(name = "message", accessMode = Schema.AccessMode.READ_ONLY, example = "Request failed schema validation", description = "The long error message.", required = true)
+  public String getMessage() {
+    return message;
+  }
+
+  public void setMessage(String message) {
+    this.message = message;
+  }
+
+  public RestErrorDto schemaValidationErrors(List<ValidationMessageDto> schemaValidationErrors) {
+    this.schemaValidationErrors = schemaValidationErrors;
+    return this;
+  }
+
+  public RestErrorDto addSchemaValidationErrorsItem(ValidationMessageDto schemaValidationErrorsItem) {
+    if (this.schemaValidationErrors == null) {
+      this.schemaValidationErrors = new ArrayList<>();
+    }
+    this.schemaValidationErrors.add(schemaValidationErrorsItem);
+    return this;
+  }
+
+  /**
+   * Validation errors against the OpenAPI schema.
+   * @return schemaValidationErrors
+  */
+  @NotNull @Valid 
+  @Schema(name = "schemaValidationErrors", description = "Validation errors against the OpenAPI schema.", required = true)
+  public List<ValidationMessageDto> getSchemaValidationErrors() {
+    return schemaValidationErrors;
+  }
+
+  public void setSchemaValidationErrors(List<ValidationMessageDto> schemaValidationErrors) {
+    this.schemaValidationErrors = schemaValidationErrors;
+  }
+
+  public RestErrorDto trace(String trace) {
+    this.trace = trace;
+    return this;
+  }
+
+  /**
+   * The stacktrace for this error.
+   * @return trace
+  */
+  
+  @Schema(name = "trace", accessMode = Schema.AccessMode.READ_ONLY, example = "com.atlassian.oai.validator.springmvc.InvalidRequestException: ...", description = "The stacktrace for this error.", required = false)
+  public String getTrace() {
+    return trace;
+  }
+
+  public void setTrace(String trace) {
+    this.trace = trace;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    RestErrorDto restError = (RestErrorDto) o;
+    return Objects.equals(this.status, restError.status) &&
+        Objects.equals(this.error, restError.error) &&
+        Objects.equals(this.path, restError.path) &&
+        Objects.equals(this.timestamp, restError.timestamp) &&
+        Objects.equals(this.message, restError.message) &&
+        Objects.equals(this.schemaValidationErrors, restError.schemaValidationErrors) &&
+        Objects.equals(this.trace, restError.trace);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(status, error, path, timestamp, message, schemaValidationErrors, trace);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class RestErrorDto {\n");
+    sb.append("    status: ").append(toIndentedString(status)).append("\n");
+    sb.append("    error: ").append(toIndentedString(error)).append("\n");
+    sb.append("    path: ").append(toIndentedString(path)).append("\n");
+    sb.append("    timestamp: ").append(toIndentedString(timestamp)).append("\n");
+    sb.append("    message: ").append(toIndentedString(message)).append("\n");
+    sb.append("    schemaValidationErrors: ").append(toIndentedString(schemaValidationErrors)).append("\n");
+    sb.append("    trace: ").append(toIndentedString(trace)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/RoleDto.java
+++ b/RoleDto.java
@@ -0,0 +1,86 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * A role.
+ */
+
+@Schema(name = "Role", description = "A role.")
+@JsonTypeName("Role")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class RoleDto {
+
+  @JsonProperty("name")
+  private String name;
+
+  public RoleDto name(String name) {
+    this.name = name;
+    return this;
+  }
+
+  /**
+   * The role's name
+   * @return name
+  */
+  @NotNull @Size(min = 1, max = 80) 
+  @Schema(name = "name", example = "admin", description = "The role's name", required = true)
+  public String getName() {
+    return name;
+  }
+
+  public void setName(String name) {
+    this.name = name;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    RoleDto role = (RoleDto) o;
+    return Objects.equals(this.name, role.name);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(name);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class RoleDto {\n");
+    sb.append("    name: ").append(toIndentedString(name)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/SpecialtyDto.java
+++ b/SpecialtyDto.java
@@ -0,0 +1,111 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * Fields of specialty of vets.
+ */
+
+@Schema(name = "Specialty", description = "Fields of specialty of vets.")
+@JsonTypeName("Specialty")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class SpecialtyDto {
+
+  @JsonProperty("id")
+  private Integer id;
+
+  @JsonProperty("name")
+  private String name;
+
+  public SpecialtyDto id(Integer id) {
+    this.id = id;
+    return this;
+  }
+
+  /**
+   * The ID of the specialty.
+   * minimum: 0
+   * @return id
+  */
+  @Min(0) 
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the specialty.", required = true)
+  public Integer getId() {
+    return id;
+  }
+
+  public void setId(Integer id) {
+    this.id = id;
+  }
+
+  public SpecialtyDto name(String name) {
+    this.name = name;
+    return this;
+  }
+
+  /**
+   * The name of the specialty.
+   * @return name
+  */
+  @NotNull @Size(min = 1, max = 80) 
+  @Schema(name = "name", example = "radiology", description = "The name of the specialty.", required = true)
+  public String getName() {
+    return name;
+  }
+
+  public void setName(String name) {
+    this.name = name;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    SpecialtyDto specialty = (SpecialtyDto) o;
+    return Objects.equals(this.id, specialty.id) &&
+        Objects.equals(this.name, specialty.name);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(id, name);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class SpecialtyDto {\n");
+    sb.append("    id: ").append(toIndentedString(id)).append("\n");
+    sb.append("    name: ").append(toIndentedString(name)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/UserDto.java
+++ b/UserDto.java
@@ -0,0 +1,170 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.util.ArrayList;
+import java.util.List;
+import org.springframework.samples.petclinic.rest.dto.RoleDto;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * An user.
+ */
+
+@Schema(name = "User", description = "An user.")
+@JsonTypeName("User")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class UserDto {
+
+  @JsonProperty("username")
+  private String username;
+
+  @JsonProperty("password")
+  private String password;
+
+  @JsonProperty("enabled")
+  private Boolean enabled;
+
+  @JsonProperty("roles")
+  @Valid
+  private List<RoleDto> roles = null;
+
+  public UserDto username(String username) {
+    this.username = username;
+    return this;
+  }
+
+  /**
+   * The username
+   * @return username
+  */
+  @NotNull @Size(min = 1, max = 80) 
+  @Schema(name = "username", example = "john.doe", description = "The username", required = true)
+  public String getUsername() {
+    return username;
+  }
+
+  public void setUsername(String username) {
+    this.username = username;
+  }
+
+  public UserDto password(String password) {
+    this.password = password;
+    return this;
+  }
+
+  /**
+   * The password
+   * @return password
+  */
+  @Size(min = 1, max = 80) 
+  @Schema(name = "password", example = "1234", description = "The password", required = false)
+  public String getPassword() {
+    return password;
+  }
+
+  public void setPassword(String password) {
+    this.password = password;
+  }
+
+  public UserDto enabled(Boolean enabled) {
+    this.enabled = enabled;
+    return this;
+  }
+
+  /**
+   * Indicates if the user is enabled
+   * @return enabled
+  */
+  
+  @Schema(name = "enabled", example = "true", description = "Indicates if the user is enabled", required = false)
+  public Boolean getEnabled() {
+    return enabled;
+  }
+
+  public void setEnabled(Boolean enabled) {
+    this.enabled = enabled;
+  }
+
+  public UserDto roles(List<RoleDto> roles) {
+    this.roles = roles;
+    return this;
+  }
+
+  public UserDto addRolesItem(RoleDto rolesItem) {
+    if (this.roles == null) {
+      this.roles = new ArrayList<>();
+    }
+    this.roles.add(rolesItem);
+    return this;
+  }
+
+  /**
+   * The roles of an user
+   * @return roles
+  */
+  @Valid 
+  @Schema(name = "roles", description = "The roles of an user", required = false)
+  public List<RoleDto> getRoles() {
+    return roles;
+  }
+
+  public void setRoles(List<RoleDto> roles) {
+    this.roles = roles;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    UserDto user = (UserDto) o;
+    return Objects.equals(this.username, user.username) &&
+        Objects.equals(this.password, user.password) &&
+        Objects.equals(this.enabled, user.enabled) &&
+        Objects.equals(this.roles, user.roles);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(username, password, enabled, roles);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class UserDto {\n");
+    sb.append("    username: ").append(toIndentedString(username)).append("\n");
+    sb.append("    password: ").append(toIndentedString(password)).append("\n");
+    sb.append("    enabled: ").append(toIndentedString(enabled)).append("\n");
+    sb.append("    roles: ").append(toIndentedString(roles)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/ValidationMessageDto.java
+++ b/ValidationMessageDto.java
@@ -0,0 +1,90 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.util.HashMap;
+import java.util.Map;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * Messages describing a validation error.
+ */
+
+@Schema(name = "ValidationMessage", description = "Messages describing a validation error.")
+@JsonTypeName("ValidationMessage")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class ValidationMessageDto extends HashMap<String, Object> {
+
+  @JsonProperty("message")
+  private String message;
+
+  public ValidationMessageDto message(String message) {
+    this.message = message;
+    return this;
+  }
+
+  /**
+   * The valiation message.
+   * @return message
+  */
+  
+  @Schema(name = "message", accessMode = Schema.AccessMode.READ_ONLY, example = "[Path '/lastName'] Instance type (null) does not match any allowed primitive type (allowed: [\"string\"])", description = "The valiation message.", required = true)
+  public String getMessage() {
+    return message;
+  }
+
+  public void setMessage(String message) {
+    this.message = message;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    ValidationMessageDto validationMessage = (ValidationMessageDto) o;
+    return Objects.equals(this.message, validationMessage.message) &&
+        super.equals(o);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(message, super.hashCode());
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class ValidationMessageDto {\n");
+    sb.append("    ").append(toIndentedString(super.toString())).append("\n");
+    sb.append("    message: ").append(toIndentedString(message)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/VetAllOfDto.java
+++ b/VetAllOfDto.java
@@ -0,0 +1,86 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * VetAllOfDto
+ */
+
+@JsonTypeName("Vet_allOf")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class VetAllOfDto {
+
+  @JsonProperty("id")
+  private Integer id;
+
+  public VetAllOfDto id(Integer id) {
+    this.id = id;
+    return this;
+  }
+
+  /**
+   * The ID of the vet.
+   * minimum: 0
+   * @return id
+  */
+  @Min(0) 
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the vet.", required = false)
+  public Integer getId() {
+    return id;
+  }
+
+  public void setId(Integer id) {
+    this.id = id;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    VetAllOfDto vetAllOf = (VetAllOfDto) o;
+    return Objects.equals(this.id, vetAllOf.id);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(id);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class VetAllOfDto {\n");
+    sb.append("    id: ").append(toIndentedString(id)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/VetDto.java
+++ b/VetDto.java
@@ -0,0 +1,173 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.util.ArrayList;
+import java.util.List;
+import org.springframework.samples.petclinic.rest.dto.SpecialtyDto;
+import org.springframework.samples.petclinic.rest.dto.VetAllOfDto;
+import org.springframework.samples.petclinic.rest.dto.VetFieldsDto;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * A veterinarian.
+ */
+
+@Schema(name = "Vet", description = "A veterinarian.")
+@JsonTypeName("Vet")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class VetDto {
+
+  @JsonProperty("firstName")
+  private String firstName;
+
+  @JsonProperty("lastName")
+  private String lastName;
+
+  @JsonProperty("specialties")
+  @Valid
+  private List<SpecialtyDto> specialties = new ArrayList<>();
+
+  @JsonProperty("id")
+  private Integer id;
+
+  public VetDto firstName(String firstName) {
+    this.firstName = firstName;
+    return this;
+  }
+
+  /**
+   * The first name of the vet.
+   * @return firstName
+  */
+  @NotNull @Pattern(regexp = "^[a-zA-Z]*$") @Size(min = 1, max = 30) 
+  @Schema(name = "firstName", example = "James", description = "The first name of the vet.", required = true)
+  public String getFirstName() {
+    return firstName;
+  }
+
+  public void setFirstName(String firstName) {
+    this.firstName = firstName;
+  }
+
+  public VetDto lastName(String lastName) {
+    this.lastName = lastName;
+    return this;
+  }
+
+  /**
+   * The last name of the vet.
+   * @return lastName
+  */
+  @NotNull @Pattern(regexp = "^[a-zA-Z]*$") @Size(min = 1, max = 30) 
+  @Schema(name = "lastName", example = "Carter", description = "The last name of the vet.", required = true)
+  public String getLastName() {
+    return lastName;
+  }
+
+  public void setLastName(String lastName) {
+    this.lastName = lastName;
+  }
+
+  public VetDto specialties(List<SpecialtyDto> specialties) {
+    this.specialties = specialties;
+    return this;
+  }
+
+  public VetDto addSpecialtiesItem(SpecialtyDto specialtiesItem) {
+    if (this.specialties == null) {
+      this.specialties = new ArrayList<>();
+    }
+    this.specialties.add(specialtiesItem);
+    return this;
+  }
+
+  /**
+   * The specialties of the vet.
+   * @return specialties
+  */
+  @NotNull @Valid 
+  @Schema(name = "specialties", description = "The specialties of the vet.", required = true)
+  public List<SpecialtyDto> getSpecialties() {
+    return specialties;
+  }
+
+  public void setSpecialties(List<SpecialtyDto> specialties) {
+    this.specialties = specialties;
+  }
+
+  public VetDto id(Integer id) {
+    this.id = id;
+    return this;
+  }
+
+  /**
+   * The ID of the vet.
+   * minimum: 0
+   * @return id
+  */
+  @Min(0) 
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the vet.", required = true)
+  public Integer getId() {
+    return id;
+  }
+
+  public void setId(Integer id) {
+    this.id = id;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    VetDto vet = (VetDto) o;
+    return Objects.equals(this.firstName, vet.firstName) &&
+        Objects.equals(this.lastName, vet.lastName) &&
+        Objects.equals(this.specialties, vet.specialties) &&
+        Objects.equals(this.id, vet.id);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(firstName, lastName, specialties, id);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class VetDto {\n");
+    sb.append("    firstName: ").append(toIndentedString(firstName)).append("\n");
+    sb.append("    lastName: ").append(toIndentedString(lastName)).append("\n");
+    sb.append("    specialties: ").append(toIndentedString(specialties)).append("\n");
+    sb.append("    id: ").append(toIndentedString(id)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/VetFieldsDto.java
+++ b/VetFieldsDto.java
@@ -0,0 +1,146 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.util.ArrayList;
+import java.util.List;
+import org.springframework.samples.petclinic.rest.dto.SpecialtyDto;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * Editable fields of a veterinarian.
+ */
+
+@Schema(name = "VetFields", description = "Editable fields of a veterinarian.")
+@JsonTypeName("VetFields")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class VetFieldsDto {
+
+  @JsonProperty("firstName")
+  private String firstName;
+
+  @JsonProperty("lastName")
+  private String lastName;
+
+  @JsonProperty("specialties")
+  @Valid
+  private List<SpecialtyDto> specialties = new ArrayList<>();
+
+  public VetFieldsDto firstName(String firstName) {
+    this.firstName = firstName;
+    return this;
+  }
+
+  /**
+   * The first name of the vet.
+   * @return firstName
+  */
+  @NotNull @Pattern(regexp = "^[a-zA-Z]*$") @Size(min = 1, max = 30) 
+  @Schema(name = "firstName", example = "James", description = "The first name of the vet.", required = true)
+  public String getFirstName() {
+    return firstName;
+  }
+
+  public void setFirstName(String firstName) {
+    this.firstName = firstName;
+  }
+
+  public VetFieldsDto lastName(String lastName) {
+    this.lastName = lastName;
+    return this;
+  }
+
+  /**
+   * The last name of the vet.
+   * @return lastName
+  */
+  @NotNull @Pattern(regexp = "^[a-zA-Z]*$") @Size(min = 1, max = 30) 
+  @Schema(name = "lastName", example = "Carter", description = "The last name of the vet.", required = true)
+  public String getLastName() {
+    return lastName;
+  }
+
+  public void setLastName(String lastName) {
+    this.lastName = lastName;
+  }
+
+  public VetFieldsDto specialties(List<SpecialtyDto> specialties) {
+    this.specialties = specialties;
+    return this;
+  }
+
+  public VetFieldsDto addSpecialtiesItem(SpecialtyDto specialtiesItem) {
+    if (this.specialties == null) {
+      this.specialties = new ArrayList<>();
+    }
+    this.specialties.add(specialtiesItem);
+    return this;
+  }
+
+  /**
+   * The specialties of the vet.
+   * @return specialties
+  */
+  @NotNull @Valid 
+  @Schema(name = "specialties", description = "The specialties of the vet.", required = true)
+  public List<SpecialtyDto> getSpecialties() {
+    return specialties;
+  }
+
+  public void setSpecialties(List<SpecialtyDto> specialties) {
+    this.specialties = specialties;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    VetFieldsDto vetFields = (VetFieldsDto) o;
+    return Objects.equals(this.firstName, vetFields.firstName) &&
+        Objects.equals(this.lastName, vetFields.lastName) &&
+        Objects.equals(this.specialties, vetFields.specialties);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(firstName, lastName, specialties);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class VetFieldsDto {\n");
+    sb.append("    firstName: ").append(toIndentedString(firstName)).append("\n");
+    sb.append("    lastName: ").append(toIndentedString(lastName)).append("\n");
+    sb.append("    specialties: ").append(toIndentedString(specialties)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/VisitAllOfDto.java
+++ b/VisitAllOfDto.java
@@ -0,0 +1,111 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * VisitAllOfDto
+ */
+
+@JsonTypeName("Visit_allOf")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class VisitAllOfDto {
+
+  @JsonProperty("id")
+  private Integer id;
+
+  @JsonProperty("petId")
+  private Integer petId;
+
+  public VisitAllOfDto id(Integer id) {
+    this.id = id;
+    return this;
+  }
+
+  /**
+   * The ID of the visit.
+   * minimum: 0
+   * @return id
+  */
+  @Min(0) 
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the visit.", required = true)
+  public Integer getId() {
+    return id;
+  }
+
+  public void setId(Integer id) {
+    this.id = id;
+  }
+
+  public VisitAllOfDto petId(Integer petId) {
+    this.petId = petId;
+    return this;
+  }
+
+  /**
+   * The ID of the pet.
+   * minimum: 0
+   * @return petId
+  */
+  @Min(0) 
+  @Schema(name = "petId", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet.", required = false)
+  public Integer getPetId() {
+    return petId;
+  }
+
+  public void setPetId(Integer petId) {
+    this.petId = petId;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    VisitAllOfDto visitAllOf = (VisitAllOfDto) o;
+    return Objects.equals(this.id, visitAllOf.id) &&
+        Objects.equals(this.petId, visitAllOf.petId);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(id, petId);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class VisitAllOfDto {\n");
+    sb.append("    id: ").append(toIndentedString(id)).append("\n");
+    sb.append("    petId: ").append(toIndentedString(petId)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/VisitDto.java
+++ b/VisitDto.java
@@ -0,0 +1,165 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.LocalDate;
+import org.springframework.format.annotation.DateTimeFormat;
+import org.springframework.samples.petclinic.rest.dto.VisitAllOfDto;
+import org.springframework.samples.petclinic.rest.dto.VisitFieldsDto;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * A booking for a vet visit.
+ */
+
+@Schema(name = "Visit", description = "A booking for a vet visit.")
+@JsonTypeName("Visit")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class VisitDto {
+
+  @JsonProperty("date")
+  @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
+  private LocalDate date;
+
+  @JsonProperty("description")
+  private String description;
+
+  @JsonProperty("id")
+  private Integer id;
+
+  @JsonProperty("petId")
+  private Integer petId;
+
+  public VisitDto date(LocalDate date) {
+    this.date = date;
+    return this;
+  }
+
+  /**
+   * The date of the visit.
+   * @return date
+  */
+  @Valid 
+  @Schema(name = "date", example = "Tue Jan 01 05:30:00 IST 2013", description = "The date of the visit.", required = false)
+  public LocalDate getDate() {
+    return date;
+  }
+
+  public void setDate(LocalDate date) {
+    this.date = date;
+  }
+
+  public VisitDto description(String description) {
+    this.description = description;
+    return this;
+  }
+
+  /**
+   * The description for the visit.
+   * @return description
+  */
+  @NotNull @Size(min = 1, max = 255) 
+  @Schema(name = "description", example = "rabies shot", description = "The description for the visit.", required = true)
+  public String getDescription() {
+    return description;
+  }
+
+  public void setDescription(String description) {
+    this.description = description;
+  }
+
+  public VisitDto id(Integer id) {
+    this.id = id;
+    return this;
+  }
+
+  /**
+   * The ID of the visit.
+   * minimum: 0
+   * @return id
+  */
+  @Min(0) 
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the visit.", required = true)
+  public Integer getId() {
+    return id;
+  }
+
+  public void setId(Integer id) {
+    this.id = id;
+  }
+
+  public VisitDto petId(Integer petId) {
+    this.petId = petId;
+    return this;
+  }
+
+  /**
+   * The ID of the pet.
+   * minimum: 0
+   * @return petId
+  */
+  @Min(0) 
+  @Schema(name = "petId", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet.", required = false)
+  public Integer getPetId() {
+    return petId;
+  }
+
+  public void setPetId(Integer petId) {
+    this.petId = petId;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    VisitDto visit = (VisitDto) o;
+    return Objects.equals(this.date, visit.date) &&
+        Objects.equals(this.description, visit.description) &&
+        Objects.equals(this.id, visit.id) &&
+        Objects.equals(this.petId, visit.petId);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(date, description, id, petId);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class VisitDto {\n");
+    sb.append("    date: ").append(toIndentedString(date)).append("\n");
+    sb.append("    description: ").append(toIndentedString(description)).append("\n");
+    sb.append("    id: ").append(toIndentedString(id)).append("\n");
+    sb.append("    petId: ").append(toIndentedString(petId)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

--- a/VisitFieldsDto.java
+++ b/VisitFieldsDto.java
@@ -0,0 +1,113 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.LocalDate;
+import org.springframework.format.annotation.DateTimeFormat;
+import java.time.OffsetDateTime;
+import javax.validation.Valid;
+import javax.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import javax.annotation.Generated;
+
+/**
+ * Editable fields of a vet visit.
+ */
+
+@Schema(name = "VisitFields", description = "Editable fields of a vet visit.")
+@JsonTypeName("VisitFields")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:04:38.621709+05:30[Asia/Kolkata]")
+public class VisitFieldsDto {
+
+  @JsonProperty("date")
+  @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
+  private LocalDate date;
+
+  @JsonProperty("description")
+  private String description;
+
+  public VisitFieldsDto date(LocalDate date) {
+    this.date = date;
+    return this;
+  }
+
+  /**
+   * The date of the visit.
+   * @return date
+  */
+  @Valid 
+  @Schema(name = "date", example = "Tue Jan 01 05:30:00 IST 2013", description = "The date of the visit.", required = false)
+  public LocalDate getDate() {
+    return date;
+  }
+
+  public void setDate(LocalDate date) {
+    this.date = date;
+  }
+
+  public VisitFieldsDto description(String description) {
+    this.description = description;
+    return this;
+  }
+
+  /**
+   * The description for the visit.
+   * @return description
+  */
+  @NotNull @Size(min = 1, max = 255) 
+  @Schema(name = "description", example = "rabies shot", description = "The description for the visit.", required = true)
+  public String getDescription() {
+    return description;
+  }
+
+  public void setDescription(String description) {
+    this.description = description;
+  }
+
+  @Override
+  public boolean equals(Object o) {
+    if (this == o) {
+      return true;
+    }
+    if (o == null || getClass() != o.getClass()) {
+      return false;
+    }
+    VisitFieldsDto visitFields = (VisitFieldsDto) o;
+    return Objects.equals(this.date, visitFields.date) &&
+        Objects.equals(this.description, visitFields.description);
+  }
+
+  @Override
+  public int hashCode() {
+    return Objects.hash(date, description);
+  }
+
+  @Override
+  public String toString() {
+    StringBuilder sb = new StringBuilder();
+    sb.append("class VisitFieldsDto {\n");
+    sb.append("    date: ").append(toIndentedString(date)).append("\n");
+    sb.append("    description: ").append(toIndentedString(description)).append("\n");
+    sb.append("}");
+    return sb.toString();
+  }
+
+  /**
+   * Convert the given object to string with each line indented by 4 spaces
+   * (except the first line).
+   */
+  private String toIndentedString(Object o) {
+    if (o == null) {
+      return "null";
+    }
+    return o.toString().replace("\n", "\n    ");
+  }
+}
+

```

## Diagnosis (written by the model; unverified, check before relying on it)

The most likely issue is that the necessary Java libraries for `javax.validation`, `javax.annotation`, and `javax.validation.constraints` are missing in your project. These packages are part of the Java EE API, which has been deprecated and removed in Java 9 and later. To resolve this, you should add the required dependencies for these packages to your `pom.xml` file. Check if you have the following dependencies:

```xml
<dependency>
    <groupId>javax.validation</groupId>
    <artifactId>validation-api</artifactId>
    <version>2.0.1.Final</version>
</dependency>
<dependency>
    <groupId>javax.annotation</groupId>
    <artifactId>javax.annotation-api</artifactId>
    <version>1.3.2</version>
</dependency>
```

Ensure that these dependencies are compatible with Spring Boot 3 and that there are no conflicts with other dependencies in your project.

## Last build error (best state)
```
[ERROR] COMPILATION ERROR : 
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-out/migrated-spring-petclinic-rest/target/generated-sources/openapi/src/main/java/org/springframework/samples/petclinic/rest/api/PettypesApi.java:[26,24] package javax.validation does not exist
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-out/migrated-spring-petclinic-rest/target/generated-sources/openapi/src/main/java/org/springframework/samples/petclinic/rest/api/PettypesApi.java:[31,24] package javax.annotation does not exist
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-out/migrated-spring-petclinic-rest/target/generated-sources/openapi/src/main/java/org/springframework/samples/petclinic/rest/api/PettypesApi.java:[33,2] cannot find symbol
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-out/migrated-spring-petclinic-rest/target/generated-sources/openapi/src/main/java/org/springframework/samples/petclinic/rest/dto/PetTypeDto.java:[11,24] package javax.validation does not exist
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-out/migrated-spring-petclinic-rest/target/generated-sources/openapi/src/main/java/org/springframework/samples/petclinic/rest/dto/PetTypeDto.java:[18,24] package javax.annotation does not exist
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-out/migrated-spring-petclinic-rest/target/generated-sources/openapi/src/main/java/org/springframework/samples/petclinic/rest/dto/PetTypeDto.java:[26,2] cannot find symbol
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-out/migrated-spring-petclinic-rest/target/generated-sources/openapi/src/main/java/org/springframework/samples/petclinic/rest/api/PettypesApi.java:[27,24] package javax.validation.constraints does not exist
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-out/migrated-spring-petclinic-rest/target/generated-sources/openapi/src/main/java/org/springframework/samples/petclinic/rest/dto/PetTypeDto.java:[12,24] package javax.validation.constraints does not exist
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-out/migrated-spring-petclinic-rest/target/generated-sources/openapi/src/main/java/org/springframework/samples/petclinic/rest/api/UsersApi.java:[26,24] package javax.validation does not exist
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-out/migrated-spring-petclinic-rest/target/generated-sources/openapi/src/main/java/org/springframework/samples/petclinic/rest/api/UsersApi.java:[31,24] package javax.annotation does not exist
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-out/migrated-spring-petclinic-rest/target/generated-sources/openapi/src/main/java/org/springframework/samples/petclinic/rest/api/UsersApi.java:[33,2] cannot find symbol
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-out/migrated-spring-petclinic-rest/target/generated-sources/openapi/src/main/java/org/springframework/samples/petclinic/rest/dto/UserDto.java:[12,24] package javax.validation does not exist
[ERROR] /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-out/migrated-spring-petclinic-rest/target/generated-sources/openapi/src/main/java/org/springframework/samples/petclinic/rest/dto/UserDto.java:[19,24] package javax.annotation does not exis
```