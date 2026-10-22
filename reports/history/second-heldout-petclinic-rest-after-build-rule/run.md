# Migration report

- App: `spring-petclinic-rest`  |  Model: `qwen2.5-coder:7b-instruct`  |  Upgrade tool: OpenRewrite (rewrite-spring 6.37.1)
- Spring Boot parent after upgrade: `3.3.13`
- Build-file rules applied by the agent (deterministic, not the model; the model can never edit the pom): openapi-generator-maven-plugin 6.0.1 -> 6.6.0; openapi-generator configOptions: useSpringBoot3 = true (generate jakarta.* code)
- Result: **NEEDS HUMAN REVIEW (tests failing)**
- Model fix rounds: 5 (max 5)
- Settings: temperature 0, seed 0, 8192-token context; output fingerprint `c57136deed0f` (identical fingerprints across runs mean identical generated code)

## Build score per run

Score = failing tests, or 1000+ compile errors. 0 means green. A run that scores worse than the best so far is rolled back.

| Run | Score | Tests passed | What happened |
|---|---|---|---|
| 1 | 4 | 168/172 | build; model fixed JpaPetRepositoryImpl.java, model fixed JpaPetTypeRepositoryImpl.java, model fixed SpringDataPetRepositoryImpl.java, model fixed SpringDataPetTypeRepositoryImpl.java, model fixed ClinicServiceImpl.java |
| 2 | 2 | 170/172 | build; model fixed JpaPetRepositoryImpl.java, model fixed JpaPetTypeRepositoryImpl.java, model fixed SpringDataPetRepositoryImpl.java, model fixed SpringDataPetTypeRepositoryImpl.java, model fixed ClinicServiceImpl.java |
| 3 | 2 | 170/172 | rolled back (score 3 is worse than 2); model fixed JpaPetRepositoryImpl.java, model fixed JpaPetTypeRepositoryImpl.java, model fixed SpringDataPetRepositoryImpl.java, model fixed SpringDataPetTypeRepositoryImpl.java, model fixed ClinicServiceImpl.java |
| 4 | 2 | 170/172 | rolled back (score 3 is worse than 2); model fixed JpaPetRepositoryImpl.java, model fixed JpaPetTypeRepositoryImpl.java, model fixed SpringDataPetRepositoryImpl.java, model fixed SpringDataPetTypeRepositoryImpl.java, model fixed ClinicServiceImpl.java |
| 5 | 2 | 170/172 | rolled back (score 3 is worse than 2); model fixed JpaPetRepositoryImpl.java, model fixed JpaPetTypeRepositoryImpl.java, model fixed SpringDataPetRepositoryImpl.java, model fixed SpringDataPetTypeRepositoryImpl.java, model fixed ClinicServiceImpl.java |
| 6 | 2 | 170/172 | rolled back (score 3 is worse than 2) |

## Test integrity

- Existing files under `src/test` (tests and test resources) and every `pom.xml` / `.mvn` file are hashed after the upgrade tool runs and again at the end. The fix loop can only write under `src/main`.
- The upgraded pom must not gain test-skipping settings (`skipTests`, `maven.test.skip`, `testFailureIgnore`, surefire `skip` or excludes).
- A passing run must execute exactly the baseline's tests: the original app ran 172 tests, 172 passed.
- Result: no violations.

The upgrade tool itself (not the model) rewrote these test files: `src/test/java/org/springframework/samples/petclinic/model/ValidatorTests.java`, `src/test/resources/application.properties`

## Security equivalence (same requests, Boot 2 build vs upgraded build)

10 checks, **2 difference(s)**, of which **0 newly accessible**. Cells show the HTTP status; changed cells show before → after. 401/403 means denied; 404 means the route was not found, which is a different problem.

| Endpoint | anonymous |
|---|---|
| `GET /petclinic/api/nothing-here` | **404 → 400** |
| `GET /petclinic/api/owners` | 200 |
| `GET /petclinic/api/owners/` | **200 → 400** |
| `GET /petclinic/api/owners/1` | 200 |
| `GET /petclinic/api/pets` | 200 |
| `GET /petclinic/api/pettypes` | 200 |
| `GET /petclinic/api/specialties` | 200 |
| `GET /petclinic/api/users` | 400 |
| `GET /petclinic/api/vets` | 200 |
| `GET /petclinic/api/visits` | 200 |

### What changed

| Request | Role | Before | After | What it means |
|---|---|---|---|---|
| `GET /petclinic/api/nothing-here` | anonymous | 404 | 400 | not found -> rejected |
| `GET /petclinic/api/owners/` | anonymous | 200 | 400 | the request is now refused by the app |

**Flagged for a human: the upgraded app answers some requests differently. Review each before deploying.**

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
@@ -74,8 +74,8 @@
 	public void delete(Pet pet) throws DataAccessException {
 		//this.em.remove(this.em.contains(pet) ? pet : this.em.merge(pet));
 		String petId = pet.getId().toString();
-		this.em.createQuery("DELETE FROM Visit visit WHERE pet_id=" + petId).executeUpdate();
-		this.em.createQuery("DELETE FROM Pet pet WHERE id=" + petId).executeUpdate();
+		this.em.createQuery("DELETE FROM Visit visit WHERE pet_id = :petId").setParameter("petId", petId).executeUpdate();
+		this.em.createQuery("DELETE FROM Pet pet WHERE id = :petId").setParameter("petId", petId).executeUpdate();
 		if (em.contains(pet)) {
 			em.remove(pet);
 		}

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
@@ -70,15 +70,23 @@
 		this.em.remove(this.em.contains(petType) ? petType : this.em.merge(petType));
 		Integer petTypeId = petType.getId();
 		
-		List<Pet> pets = this.em.createQuery("SELECT pet FROM Pet pet WHERE type_id=" + petTypeId).getResultList();
+		List<Pet> pets = this.em.createQuery("SELECT pet FROM Pet pet WHERE type_id = :petTypeId", Pet.class)
+				.setParameter("petTypeId", petTypeId)
+				.getResultList();
 		for (Pet pet : pets){
 			List<Visit> visits = pet.getVisits();
 			for (Visit visit : visits){
-				this.em.createQuery("DELETE FROM Visit visit WHERE id=" + visit.getId()).executeUpdate();
+				this.em.createQuery("DELETE FROM Visit visit WHERE id = :visitId", Visit.class)
+						.setParameter("visitId", visit.getId())
+						.executeUpdate();
 			}
-			this.em.createQuery("DELETE FROM Pet pet WHERE id=" + pet.getId()).executeUpdate();
+			this.em.createQuery("DELETE FROM Pet pet WHERE id = :petId", Pet.class)
+					.setParameter("petId", pet.getId())
+					.executeUpdate();
 		}
-		this.em.createQuery("DELETE FROM PetType pettype WHERE id=" + petTypeId).executeUpdate();
+		this.em.createQuery("DELETE FROM PetType pettype WHERE id = :petTypeId", PetType.class)
+				.setParameter("petTypeId", petTypeId)
+				.executeUpdate();
 	}
 
 }

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
@@ -36,8 +36,8 @@
 	@Override
 	public void delete(Pet pet) {
 		String petId = pet.getId().toString();
-		this.em.createQuery("DELETE FROM Visit visit WHERE pet_id=" + petId).executeUpdate();
-		this.em.createQuery("DELETE FROM Pet pet WHERE id=" + petId).executeUpdate();
+		this.em.createQuery("DELETE FROM Visit visit WHERE pet.id=" + petId).executeUpdate();
+		this.em.createQuery("DELETE FROM Pet pet WHERE pet.id=" + petId).executeUpdate();
         if (em.contains(pet)) {
             em.remove(pet);
         }

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
@@ -42,15 +42,15 @@
         this.em.remove(this.em.contains(petType) ? petType : this.em.merge(petType));
 		Integer petTypeId = petType.getId();
 		
-		List<Pet> pets = this.em.createQuery("SELECT pet FROM Pet pet WHERE type_id=" + petTypeId).getResultList();
+		List<Pet> pets = this.em.createQuery("SELECT pet FROM Pet pet WHERE pet.type.id=" + petTypeId).getResultList();
 		for (Pet pet : pets){
 			List<Visit> visits = pet.getVisits();
 			for (Visit visit : visits){
-				this.em.createQuery("DELETE FROM Visit visit WHERE id=" + visit.getId()).executeUpdate();
+				this.em.createQuery("DELETE FROM Visit visit WHERE visit.id=" + visit.getId()).executeUpdate();
 			}
-			this.em.createQuery("DELETE FROM Pet pet WHERE id=" + pet.getId()).executeUpdate();
+			this.em.createQuery("DELETE FROM Pet pet WHERE pet.id=" + pet.getId()).executeUpdate();
 		}
-		this.em.createQuery("DELETE FROM PetType pettype WHERE id=" + petTypeId).executeUpdate();
+		this.em.createQuery("DELETE FROM PetType pettype WHERE pettype.id=" + petTypeId).executeUpdate();
 	}
 
 }

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
@@ -52,239 +52,232 @@
     private OwnerRepository ownerRepository;
     private VisitRepository visitRepository;
     private SpecialtyRepository specialtyRepository;
-	private PetTypeRepository petTypeRepository;
+    private PetTypeRepository petTypeRepository;
 
     @Autowired
-     public ClinicServiceImpl(
-       		 PetRepository petRepository,
-    		 VetRepository vetRepository,
-    		 OwnerRepository ownerRepository,
-    		 VisitRepository visitRepository,
-    		 SpecialtyRepository specialtyRepository,
-			 PetTypeRepository petTypeRepository) {
+    public ClinicServiceImpl(
+            PetRepository petRepository,
+            VetRepository vetRepository,
+            OwnerRepository ownerRepository,
+            VisitRepository visitRepository,
+            SpecialtyRepository specialtyRepository,
+            PetTypeRepository petTypeRepository) {
         this.petRepository = petRepository;
         this.vetRepository = vetRepository;
         this.ownerRepository = ownerRepository;
         this.visitRepository = visitRepository;
         this.specialtyRepository = specialtyRepository;
-		this.petTypeRepository = petTypeRepository;
-    }
-
-	@Override
-	@Transactional(readOnly = true)
-	public Collection<Pet> findAllPets() throws DataAccessException {
-		return petRepository.findAll();
-	}
-
-	@Override
-	@Transactional
-	public void deletePet(Pet pet) throws DataAccessException {
-		petRepository.delete(pet);
-	}
-
-	@Override
-	@Transactional(readOnly = true)
-	public Visit findVisitById(int visitId) throws DataAccessException {
-		Visit visit = null;
-		try {
-			visit = visitRepository.findById(visitId);
-		} catch (ObjectRetrievalFailureException|EmptyResultDataAccessException e) {
-		// just ignore not found exceptions for Jdbc/Jpa realization
-			return null;
-		}
-		return visit;
-	}
-
-	@Override
-	@Transactional(readOnly = true)
-	public Collection<Visit> findAllVisits() throws DataAccessException {
-		return visitRepository.findAll();
-	}
-
-	@Override
-	@Transactional
-	public void deleteVisit(Visit visit) throws DataAccessException {
-		visitRepository.delete(visit);
-	}
-
-	@Override
-	@Transactional(readOnly = true)
-	public Vet findVetById(int id) throws DataAccessException {
-		Vet vet = null;
-		try {
-			vet = vetRepository.findById(id);
-		} catch (ObjectRetrievalFailureException|EmptyResultDataAccessException e) {
-		// just ignore not found exceptions for Jdbc/Jpa realization
-			return null;
-		}
-		return vet;
-	}
-
-	@Override
-	@Transactional(readOnly = true)
-	public Collection<Vet> findAllVets() throws DataAccessException {
-		return vetRepository.findAll();
-	}
-
-	@Override
-	@Transactional
-	public void saveVet(Vet vet) throws DataAccessException {
-		vetRepository.save(vet);
-	}
-
-	@Override
-	@Transactional
-	public void deleteVet(Vet vet) throws DataAccessException {
-		vetRepository.delete(vet);
-	}
-
-	@Override
-	@Transactional(readOnly = true)
-	public Collection<Owner> findAllOwners() throws DataAccessException {
-		return ownerRepository.findAll();
-	}
-
-	@Override
-	@Transactional
-	public void deleteOwner(Owner owner) throws DataAccessException {
-		ownerRepository.delete(owner);
-	}
-
-	@Override
-	@Transactional(readOnly = true)
-	public PetType findPetTypeById(int petTypeId) {
-		PetType petType = null;
-		try {
-			petType = petTypeRepository.findById(petTypeId);
-		} catch (ObjectRetrievalFailureException|EmptyResultDataAccessException e) {
-		// just ignore not found exceptions for Jdbc/Jpa realization
-			return null;
-		}
-		return petType;
-	}
-
-	@Override
-	@Transactional(readOnly = true)
-	public Collection<PetType> findAllPetTypes() throws DataAccessException {
-		return petTypeRepository.findAll();
-	}
-
-	@Override
-	@Transactional
-	public void savePetType(PetType petType) throws DataAccessException {
-		petTypeRepository.save(petType);
-	}
-
-	@Override
-	@Transactional
-	public void deletePetType(PetType petType) throws DataAccessException {
-		petTypeRepository.delete(petType);
-	}
-
-	@Override
-	@Transactional(readOnly = true)
-	public Specialty findSpecialtyById(int specialtyId) {
-		Specialty specialty = null;
-		try {
-			specialty = specialtyRepository.findById(specialtyId);
-		} catch (ObjectRetrievalFailureException|EmptyResultDataAccessException e) {
-		// just ignore not found exceptions for Jdbc/Jpa realization
-			return null;
-		}
-		return specialty;
-	}
-
-	@Override
-	@Transactional(readOnly = true)
-	public Collection<Specialty> findAllSpecialties() throws DataAccessException {
-		return specialtyRepository.findAll();
-	}
-
-	@Override
-	@Transactional
-	public void saveSpecialty(Specialty specialty) throws DataAccessException {
-		specialtyRepository.save(specialty);
-	}
-
-	@Override
-	@Transactional
-	public void deleteSpecialty(Specialty specialty) throws DataAccessException {
-		specialtyRepository.delete(specialty);
-	}
-
-	@Override
-	@Transactional(readOnly = true)
-	public Collection<PetType> findPetTypes() throws DataAccessException {
-		return petRepository.findPetTypes();
-	}
-
-	@Override
-	@Transactional(readOnly = true)
-	public Owner findOwnerById(int id) throws DataAccessException {
-		Owner owner = null;
-		try {
-			owner = ownerRepository.findById(id);
-		} catch (ObjectRetrievalFailureException|EmptyResultDataAccessException e) {
-		// just ignore not found exceptions for Jdbc/Jpa realization
-			return null;
-		}
-		return owner;
-	}
-
-	@Override
-	@Transactional(readOnly = true)
-	public Pet findPetById(int id) throws DataAccessException {
-		Pet pet = null;
-		try {
-			pet = petRepository.findById(id);
-		} catch (ObjectRetrievalFailureException|EmptyResultDataAccessException e) {
-		// just ignore not found exceptions for Jdbc/Jpa realization
-			return null;
-		}
-		return pet;
-	}
-
-	@Override
-	@Transactional
-	public void savePet(Pet pet) throws DataAccessException {
-		petRepository.save(pet);
-
-	}
-
-	@Override
-	@Transactional
-	public void saveVisit(Visit visit) throws DataAccessException {
-		visitRepository.save(visit);
-
-	}
-
-	@Override
-	@Transactional(readOnly = true)
+        this.petTypeRepository = petTypeRepository;
+    }
+
+    @Override
+    @Transactional(readOnly = true)
+    public Collection<Pet> findAllPets() throws DataAccessException {
+        return petRepository.findAll();
+    }
+
+    @Override
+    @Transactional
+    public void deletePet(Pet pet) throws DataAccessException {
+        petRepository.delete(pet);
+    }
+
+    @Override
+    @Transactional(readOnly = true)
+    public Visit findVisitById(int visitId) throws DataAccessException {
+        Visit visit = null;
+        try {
+            visit = visitRepository.findById(visitId);
+        } catch (ObjectRetrievalFailureException | EmptyResultDataAccessException e) {
+            // just ignore not found exceptions for Jdbc/Jpa realization
+            return null;
+        }
+        return visit;
+    }
+
+    @Override
+    @Transactional(readOnly = true)
+    public Collection<Visit> findAllVisits() throws DataAccessException {
+        return visitRepository.findAll();
+    }
+
+    @Override
+    @Transactional
+    public void deleteVisit(Visit visit) throws DataAccessException {
+        visitRepository.delete(visit);
+    }
+
+    @Override
+    @Transactional(readOnly = true)
+    public Vet findVetById(int id) throws DataAccessException {
+        Vet vet = null;
+        try {
+            vet = vetRepository.findById(id);
+        } catch (ObjectRetrievalFailureException | EmptyResultDataAccessException e) {
+            // just ignore not found exceptions for Jdbc/Jpa realization
+            return null;
+        }
+        return vet;
+    }
+
+    @Override
+    @Transactional(readOnly = true)
+    public Collection<Vet> findAllVets() throws DataAccessException {
+        return vetRepository.findAll();
+    }
+
+    @Override
+    @Transactional
+    public void saveVet(Vet vet) throws DataAccessException {
+        vetRepository.save(vet);
+    }
+
+    @Override
+    @Transactional
+    public void deleteVet(Vet vet) throws DataAccessException {
+        vetRepository.delete(vet);
+    }
+
+    @Override
+    @Transactional(readOnly = true)
+    public Collection<Owner> findAllOwners() throws DataAccessException {
+        return ownerRepository.findAll();
+    }
+
+    @Override
+    @Transactional
+    public void deleteOwner(Owner owner) throws DataAccessException {
+        ownerRepository.delete(owner);
+    }
+
+    @Override
+    @Transactional(readOnly = true)
+    public PetType findPetTypeById(int petTypeId) {
+        PetType petType = null;
+        try {
+            petType = petTypeRepository.findById(petTypeId);
+        } catch (ObjectRetrievalFailureException | EmptyResultDataAccessException e) {
+            // just ignore not found exceptions for Jdbc/Jpa realization
+            return null;
+        }
+        return petType;
+    }
+
+    @Override
+    @Transactional(readOnly = true)
+    public Collection<PetType> findAllPetTypes() throws DataAccessException {
+        return petTypeRepository.findAll();
+    }
+
+    @Override
+    @Transactional
+    public void savePetType(PetType petType) throws DataAccessException {
+        petTypeRepository.save(petType);
+    }
+
+    @Override
+    @Transactional
+    public void deletePetType(PetType petType) throws DataAccessException {
+        petTypeRepository.delete(petType);
+    }
+
+    @Override
+    @Transactional(readOnly = true)
+    public Specialty findSpecialtyById(int specialtyId) {
+        Specialty specialty = null;
+        try {
+            specialty = specialtyRepository.findById(specialtyId);
+        } catch (ObjectRetrievalFailureException | EmptyResultDataAccessException e) {
+            // just ignore not found exceptions for Jdbc/Jpa realization
+            return null;
+        }
+        return specialty;
+    }
+
+    @Override
+    @Transactional(readOnly = true)
+    public Collection<Specialty> findAllSpecialties() throws DataAccessException {
+        return specialtyRepository.findAll();
+    }
+
+    @Override
+    @Transactional
+    public void saveSpecialty(Specialty specialty) throws DataAccessException {
+        specialtyRepository.save(specialty);
+    }
+
+    @Override
+    @Transactional
+    public void deleteSpecialty(Specialty specialty) throws DataAccessException {
+        specialtyRepository.delete(specialty);
+    }
+
+    @Override
+    @Transactional(readOnly = true)
+    public Collection<PetType> findPetTypes() throws DataAccessException {
+        return petRepository.findPetTypes();
+    }
+
+    @Override
+    @Transactional(readOnly = true)
+    public Owner findOwnerById(int id) throws DataAccessException {
+        Owner owner = null;
+        try {
+            owner = ownerRepository.findById(id);
+        } catch (ObjectRetrievalFailureException | EmptyResultDataAccessException e) {
+            // just ignore not found exceptions for Jdbc/Jpa realization
+            return null;
+        }
+        return owner;
+    }
+
+    @Override
+    @Transactional(readOnly = true)
+    public Pet findPetById(int id) throws DataAccessException {
+        Pet pet = null;
+        try {
+            pet = petRepository.findById(id);
+        } catch (ObjectRetrievalFailureException | EmptyResultDataAccessException e) {
+            // just ignore not found exceptions for Jdbc/Jpa realization
+            return null;
+        }
+        return pet;
+    }
+
+    @Override
+    @Transactional
+    public void savePet(Pet pet) throws DataAccessException {
+        petRepository.save(pet);
+    }
+
+    @Override
+    @Transactional
+    public void saveVisit(Visit visit) throws DataAccessException {
+        visitRepository.save(visit);
+    }
+
+    @Override
+    @Transactional(readOnly = true)
     @Cacheable(value = "vets")
-	public Collection<Vet> findVets() throws DataAccessException {
-		return vetRepository.findAll();
-	}
-
-	@Override
-	@Transactional
-	public void saveOwner(Owner owner) throws DataAccessException {
-		ownerRepository.save(owner);
-
-	}
-
-	@Override
-	@Transactional(readOnly = true)
-	public Collection<Owner> findOwnerByLastName(String lastName) throws DataAccessException {
-		return ownerRepository.findByLastName(lastName);
-	}
-
-	@Override
-	@Transactional(readOnly = true)
-	public Collection<Visit> findVisitsByPetId(int petId) {
-		return visitRepository.findByPetId(petId);
-	}
-
-
-
-
+    public Collection<Vet> findVets() throws DataAccessException {
+        return vetRepository.findAll();
+    }
+
+    @Override
+    @Transactional
+    public void saveOwner(Owner owner) throws DataAccessException {
+        ownerRepository.save(owner);
+    }
+
+    @Override
+    @Transactional(readOnly = true)
+    public Collection<Owner> findOwnerByLastName(String lastName) throws DataAccessException {
+        return ownerRepository.findByLastName(lastName);
+    }
+
+    @Override
+    @Transactional(readOnly = true)
+    public Collection<Visit> findVisitsByPetId(int petId) {
+        return visitRepository.findByPetId(petId);
+    }
 }

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
+import jakarta.servlet.http.HttpServletResponse;
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
@@ -0,0 +1,81 @@
+/**
+ * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.6.0).
+ * https://openapi-generator.tech
+ * Do not edit the class manually.
+ */
+package org.springframework.samples.petclinic.rest.api;
+
+import org.springframework.samples.petclinic.rest.dto.RestErrorDto;
+import io.swagger.v3.oas.annotations.ExternalDocumentation;
+import io.swagger.v3.oas.annotations.Operation;
+import io.swagger.v3.oas.annotations.Parameter;
+import io.swagger.v3.oas.annotations.Parameters;
+import io.swagger.v3.oas.annotations.media.ArraySchema;
+import io.swagger.v3.oas.annotations.media.Content;
+import io.swagger.v3.oas.annotations.media.Schema;
+import io.swagger.v3.oas.annotations.responses.ApiResponse;
+import io.swagger.v3.oas.annotations.security.SecurityRequirement;
+import io.swagger.v3.oas.annotations.tags.Tag;
+import io.swagger.v3.oas.annotations.enums.ParameterIn;
+import org.springframework.http.HttpStatus;
+import org.springframework.http.MediaType;
+import org.springframework.http.ResponseEntity;
+import org.springframework.validation.annotation.Validated;
+import org.springframework.web.bind.annotation.*;
+import org.springframework.web.context.request.NativeWebRequest;
+import org.springframework.web.multipart.MultipartFile;
+
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import jakarta.annotation.Generated;
+
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+@Validated
+@Tag(name = "failing", description = "Endpoint which always returns an error.")
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
+        description = "Produces sample error response.",
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
@@ -0,0 +1,521 @@
+/**
+ * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.6.0).
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
+import io.swagger.v3.oas.annotations.ExternalDocumentation;
+import io.swagger.v3.oas.annotations.Operation;
+import io.swagger.v3.oas.annotations.Parameter;
+import io.swagger.v3.oas.annotations.Parameters;
+import io.swagger.v3.oas.annotations.media.ArraySchema;
+import io.swagger.v3.oas.annotations.media.Content;
+import io.swagger.v3.oas.annotations.media.Schema;
+import io.swagger.v3.oas.annotations.responses.ApiResponse;
+import io.swagger.v3.oas.annotations.security.SecurityRequirement;
+import io.swagger.v3.oas.annotations.tags.Tag;
+import io.swagger.v3.oas.annotations.enums.ParameterIn;
+import org.springframework.http.HttpStatus;
+import org.springframework.http.MediaType;
+import org.springframework.http.ResponseEntity;
+import org.springframework.validation.annotation.Validated;
+import org.springframework.web.bind.annotation.*;
+import org.springframework.web.context.request.NativeWebRequest;
+import org.springframework.web.multipart.MultipartFile;
+
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import jakarta.annotation.Generated;
+
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+@Validated
+@Tag(name = "owner", description = "Endpoints related to pet owners.")
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
+        description = "Records the details of a new pet owner.",
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
+        description = "Records the details of a new pet.",
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
+        @Min(0) @Parameter(name = "ownerId", description = "The ID of the pet owner.", required = true, in = ParameterIn.PATH) @PathVariable("ownerId") Integer ownerId,
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
+        description = "Records the details of a new vet visit.",
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
+        @Min(0) @Parameter(name = "ownerId", description = "The ID of the pet owner.", required = true, in = ParameterIn.PATH) @PathVariable("ownerId") Integer ownerId,
+        @Min(0) @Parameter(name = "petId", description = "The ID of the pet.", required = true, in = ParameterIn.PATH) @PathVariable("petId") Integer petId,
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
+        description = "Returns the owner or a 404 error.",
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
+        @Min(0) @Parameter(name = "ownerId", description = "The ID of the owner.", required = true, in = ParameterIn.PATH) @PathVariable("ownerId") Integer ownerId
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
+        description = "Returns the pet owner or a 404 error.",
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
+        @Min(0) @Parameter(name = "ownerId", description = "The ID of the pet owner.", required = true, in = ParameterIn.PATH) @PathVariable("ownerId") Integer ownerId
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
+        description = "Returns the pet or a 404 error.",
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
+        @Min(0) @Parameter(name = "ownerId", description = "The ID of the pet owner.", required = true, in = ParameterIn.PATH) @PathVariable("ownerId") Integer ownerId,
+        @Min(0) @Parameter(name = "petId", description = "The ID of the pet.", required = true, in = ParameterIn.PATH) @PathVariable("petId") Integer petId
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
+        description = "Returns an array of pet owners.",
+        tags = { "owner" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Owner details found and returned.", content = {
+                @Content(mediaType = "application/json", array = @ArraySchema(schema = @Schema(implementation = OwnerDto.class)))
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
+        @Parameter(name = "lastName", description = "Last name.", in = ParameterIn.QUERY) @Valid @RequestParam(value = "lastName", required = false) String lastName
+    ) {
+        getRequest().ifPresent(request -> {
+            for (MediaType mediaType: MediaType.parseMediaTypes(request.getHeader("Accept"))) {
+                if (mediaType.isCompatibleWith(MediaType.valueOf("application/json"))) {
+                    String exampleString = "[ null, null ]";
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
+        description = "Updates the pet owner record with the specified details.",
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
+        @Min(0) @Parameter(name = "ownerId", description = "The ID of the pet owner.", required = true, in = ParameterIn.PATH) @PathVariable("ownerId") Integer ownerId,
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
+        description = "Updates the pet record with the specified details.",
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
+        @Min(0) @Parameter(name = "ownerId", description = "The ID of the pet owner.", required = true, in = ParameterIn.PATH) @PathVariable("ownerId") Integer ownerId,
+        @Min(0) @Parameter(name = "petId", description = "The ID of the pet.", required = true, in = ParameterIn.PATH) @PathVariable("petId") Integer petId,
+        @Parameter(name = "PetFieldsDto", description = "The pet details to use for the update.", required = true) @Valid @RequestBody PetFieldsDto petFieldsDto
+    ) {
+        return new ResponseEntity<>(HttpStatus.NOT_IMPLEMENTED);
+
+    }
+
+}

--- a/PetsApi.java
+++ b/PetsApi.java
@@ -0,0 +1,309 @@
+/**
+ * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.6.0).
+ * https://openapi-generator.tech
+ * Do not edit the class manually.
+ */
+package org.springframework.samples.petclinic.rest.api;
+
+import org.springframework.samples.petclinic.rest.dto.PetDto;
+import org.springframework.samples.petclinic.rest.dto.RestErrorDto;
+import io.swagger.v3.oas.annotations.ExternalDocumentation;
+import io.swagger.v3.oas.annotations.Operation;
+import io.swagger.v3.oas.annotations.Parameter;
+import io.swagger.v3.oas.annotations.Parameters;
+import io.swagger.v3.oas.annotations.media.ArraySchema;
+import io.swagger.v3.oas.annotations.media.Content;
+import io.swagger.v3.oas.annotations.media.Schema;
+import io.swagger.v3.oas.annotations.responses.ApiResponse;
+import io.swagger.v3.oas.annotations.security.SecurityRequirement;
+import io.swagger.v3.oas.annotations.tags.Tag;
+import io.swagger.v3.oas.annotations.enums.ParameterIn;
+import org.springframework.http.HttpStatus;
+import org.springframework.http.MediaType;
+import org.springframework.http.ResponseEntity;
+import org.springframework.validation.annotation.Validated;
+import org.springframework.web.bind.annotation.*;
+import org.springframework.web.context.request.NativeWebRequest;
+import org.springframework.web.multipart.MultipartFile;
+
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import jakarta.annotation.Generated;
+
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+@Validated
+@Tag(name = "pet", description = "Endpoints related to pets.")
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
+        description = "Creates a pet .",
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
+        description = "Returns the pet or a 404 error.",
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
+        @Min(0) @Parameter(name = "petId", description = "The ID of the pet.", required = true, in = ParameterIn.PATH) @PathVariable("petId") Integer petId
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
+        description = "Returns the pet  or a 404 error.",
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
+        @Min(0) @Parameter(name = "petId", description = "The ID of the pet.", required = true, in = ParameterIn.PATH) @PathVariable("petId") Integer petId
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
+        description = "Returns an array of pet .",
+        tags = { "pet" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Pet types found and returned.", content = {
+                @Content(mediaType = "application/json", array = @ArraySchema(schema = @Schema(implementation = PetDto.class)))
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
+                    String exampleString = "[ null, null ]";
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
+        description = "Returns the pet or a 404 error.",
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
+        @Min(0) @Parameter(name = "petId", description = "The ID of the pet.", required = true, in = ParameterIn.PATH) @PathVariable("petId") Integer petId,
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
@@ -0,0 +1,309 @@
+/**
+ * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.6.0).
+ * https://openapi-generator.tech
+ * Do not edit the class manually.
+ */
+package org.springframework.samples.petclinic.rest.api;
+
+import org.springframework.samples.petclinic.rest.dto.PetTypeDto;
+import org.springframework.samples.petclinic.rest.dto.RestErrorDto;
+import io.swagger.v3.oas.annotations.ExternalDocumentation;
+import io.swagger.v3.oas.annotations.Operation;
+import io.swagger.v3.oas.annotations.Parameter;
+import io.swagger.v3.oas.annotations.Parameters;
+import io.swagger.v3.oas.annotations.media.ArraySchema;
+import io.swagger.v3.oas.annotations.media.Content;
+import io.swagger.v3.oas.annotations.media.Schema;
+import io.swagger.v3.oas.annotations.responses.ApiResponse;
+import io.swagger.v3.oas.annotations.security.SecurityRequirement;
+import io.swagger.v3.oas.annotations.tags.Tag;
+import io.swagger.v3.oas.annotations.enums.ParameterIn;
+import org.springframework.http.HttpStatus;
+import org.springframework.http.MediaType;
+import org.springframework.http.ResponseEntity;
+import org.springframework.validation.annotation.Validated;
+import org.springframework.web.bind.annotation.*;
+import org.springframework.web.context.request.NativeWebRequest;
+import org.springframework.web.multipart.MultipartFile;
+
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import jakarta.annotation.Generated;
+
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
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
+        description = "Creates a pet type .",
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
+        description = "Returns the pet type or a 404 error.",
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
+        @Min(0) @Parameter(name = "petTypeId", description = "The ID of the pet type.", required = true, in = ParameterIn.PATH) @PathVariable("petTypeId") Integer petTypeId
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
+        description = "Returns the pet type or a 404 error.",
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
+        @Min(0) @Parameter(name = "petTypeId", description = "The ID of the pet type.", required = true, in = ParameterIn.PATH) @PathVariable("petTypeId") Integer petTypeId
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
+        description = "Returns an array of pet types.",
+        tags = { "pettypes" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Pet types found and returned.", content = {
+                @Content(mediaType = "application/json", array = @ArraySchema(schema = @Schema(implementation = PetTypeDto.class)))
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
+                    String exampleString = "[ null, null ]";
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
+        description = "Returns the pet type or a 404 error.",
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
+        @Min(0) @Parameter(name = "petTypeId", description = "The ID of the pet type.", required = true, in = ParameterIn.PATH) @PathVariable("petTypeId") Integer petTypeId,
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
@@ -0,0 +1,309 @@
+/**
+ * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.6.0).
+ * https://openapi-generator.tech
+ * Do not edit the class manually.
+ */
+package org.springframework.samples.petclinic.rest.api;
+
+import org.springframework.samples.petclinic.rest.dto.RestErrorDto;
+import org.springframework.samples.petclinic.rest.dto.SpecialtyDto;
+import io.swagger.v3.oas.annotations.ExternalDocumentation;
+import io.swagger.v3.oas.annotations.Operation;
+import io.swagger.v3.oas.annotations.Parameter;
+import io.swagger.v3.oas.annotations.Parameters;
+import io.swagger.v3.oas.annotations.media.ArraySchema;
+import io.swagger.v3.oas.annotations.media.Content;
+import io.swagger.v3.oas.annotations.media.Schema;
+import io.swagger.v3.oas.annotations.responses.ApiResponse;
+import io.swagger.v3.oas.annotations.security.SecurityRequirement;
+import io.swagger.v3.oas.annotations.tags.Tag;
+import io.swagger.v3.oas.annotations.enums.ParameterIn;
+import org.springframework.http.HttpStatus;
+import org.springframework.http.MediaType;
+import org.springframework.http.ResponseEntity;
+import org.springframework.validation.annotation.Validated;
+import org.springframework.web.bind.annotation.*;
+import org.springframework.web.context.request.NativeWebRequest;
+import org.springframework.web.multipart.MultipartFile;
+
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import jakarta.annotation.Generated;
+
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+@Validated
+@Tag(name = "specialty", description = "the specialty API")
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
+        description = "Creates a specialty .",
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
+        description = "Returns the specialty or a 404 error.",
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
+        @Min(0) @Parameter(name = "specialtyId", description = "The ID of the specialty.", required = true, in = ParameterIn.PATH) @PathVariable("specialtyId") Integer specialtyId
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
+        description = "Returns the specialty or a 404 error.",
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
+        @Min(0) @Parameter(name = "specialtyId", description = "The ID of the pet.", required = true, in = ParameterIn.PATH) @PathVariable("specialtyId") Integer specialtyId
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
+        description = "Returns an array of specialty .",
+        tags = { "specialty" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Specialties found and returned.", content = {
+                @Content(mediaType = "application/json", array = @ArraySchema(schema = @Schema(implementation = SpecialtyDto.class)))
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
+                    String exampleString = "[ { \"name\" : \"radiology\", \"id\" : 1 }, { \"name\" : \"radiology\", \"id\" : 1 } ]";
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
+        description = "Returns the specialty or a 404 error.",
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
+        @Min(0) @Parameter(name = "specialtyId", description = "The ID of the specialty.", required = true, in = ParameterIn.PATH) @PathVariable("specialtyId") Integer specialtyId,
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
@@ -0,0 +1,99 @@
+/**
+ * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.6.0).
+ * https://openapi-generator.tech
+ * Do not edit the class manually.
+ */
+package org.springframework.samples.petclinic.rest.api;
+
+import org.springframework.samples.petclinic.rest.dto.RestErrorDto;
+import org.springframework.samples.petclinic.rest.dto.UserDto;
+import io.swagger.v3.oas.annotations.ExternalDocumentation;
+import io.swagger.v3.oas.annotations.Operation;
+import io.swagger.v3.oas.annotations.Parameter;
+import io.swagger.v3.oas.annotations.Parameters;
+import io.swagger.v3.oas.annotations.media.ArraySchema;
+import io.swagger.v3.oas.annotations.media.Content;
+import io.swagger.v3.oas.annotations.media.Schema;
+import io.swagger.v3.oas.annotations.responses.ApiResponse;
+import io.swagger.v3.oas.annotations.security.SecurityRequirement;
+import io.swagger.v3.oas.annotations.tags.Tag;
+import io.swagger.v3.oas.annotations.enums.ParameterIn;
+import org.springframework.http.HttpStatus;
+import org.springframework.http.MediaType;
+import org.springframework.http.ResponseEntity;
+import org.springframework.validation.annotation.Validated;
+import org.springframework.web.bind.annotation.*;
+import org.springframework.web.context.request.NativeWebRequest;
+import org.springframework.web.multipart.MultipartFile;
+
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import jakarta.annotation.Generated;
+
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+@Validated
+@Tag(name = "user", description = "Endpoints related to users.")
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
+        description = "Creates a user.",
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
@@ -0,0 +1,309 @@
+/**
+ * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.6.0).
+ * https://openapi-generator.tech
+ * Do not edit the class manually.
+ */
+package org.springframework.samples.petclinic.rest.api;
+
+import org.springframework.samples.petclinic.rest.dto.RestErrorDto;
+import org.springframework.samples.petclinic.rest.dto.VetDto;
+import io.swagger.v3.oas.annotations.ExternalDocumentation;
+import io.swagger.v3.oas.annotations.Operation;
+import io.swagger.v3.oas.annotations.Parameter;
+import io.swagger.v3.oas.annotations.Parameters;
+import io.swagger.v3.oas.annotations.media.ArraySchema;
+import io.swagger.v3.oas.annotations.media.Content;
+import io.swagger.v3.oas.annotations.media.Schema;
+import io.swagger.v3.oas.annotations.responses.ApiResponse;
+import io.swagger.v3.oas.annotations.security.SecurityRequirement;
+import io.swagger.v3.oas.annotations.tags.Tag;
+import io.swagger.v3.oas.annotations.enums.ParameterIn;
+import org.springframework.http.HttpStatus;
+import org.springframework.http.MediaType;
+import org.springframework.http.ResponseEntity;
+import org.springframework.validation.annotation.Validated;
+import org.springframework.web.bind.annotation.*;
+import org.springframework.web.context.request.NativeWebRequest;
+import org.springframework.web.multipart.MultipartFile;
+
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import jakarta.annotation.Generated;
+
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+@Validated
+@Tag(name = "vet", description = "Endpoints related to vets.")
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
+        description = "Creates a vet .",
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
+        description = "Returns the vet or a 404 error.",
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
+        @Min(0) @Parameter(name = "vetId", description = "The ID of the vet.", required = true, in = ParameterIn.PATH) @PathVariable("vetId") Integer vetId
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
+        description = "Returns the vet or a 404 error.",
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
+        @Min(0) @Parameter(name = "vetId", description = "The ID of the vet.", required = true, in = ParameterIn.PATH) @PathVariable("vetId") Integer vetId
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
+        description = "Returns an array of vets.",
+        tags = { "vet" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "Vets found and returned.", content = {
+                @Content(mediaType = "application/json", array = @ArraySchema(schema = @Schema(implementation = VetDto.class)))
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
+                    String exampleString = "[ null, null ]";
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
+        description = "Returns the vet or a 404 error.",
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
+        @Min(0) @Parameter(name = "vetId", description = "The ID of the vet.", required = true, in = ParameterIn.PATH) @PathVariable("vetId") Integer vetId,
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
@@ -0,0 +1,309 @@
+/**
+ * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech) (6.6.0).
+ * https://openapi-generator.tech
+ * Do not edit the class manually.
+ */
+package org.springframework.samples.petclinic.rest.api;
+
+import org.springframework.samples.petclinic.rest.dto.RestErrorDto;
+import org.springframework.samples.petclinic.rest.dto.VisitDto;
+import io.swagger.v3.oas.annotations.ExternalDocumentation;
+import io.swagger.v3.oas.annotations.Operation;
+import io.swagger.v3.oas.annotations.Parameter;
+import io.swagger.v3.oas.annotations.Parameters;
+import io.swagger.v3.oas.annotations.media.ArraySchema;
+import io.swagger.v3.oas.annotations.media.Content;
+import io.swagger.v3.oas.annotations.media.Schema;
+import io.swagger.v3.oas.annotations.responses.ApiResponse;
+import io.swagger.v3.oas.annotations.security.SecurityRequirement;
+import io.swagger.v3.oas.annotations.tags.Tag;
+import io.swagger.v3.oas.annotations.enums.ParameterIn;
+import org.springframework.http.HttpStatus;
+import org.springframework.http.MediaType;
+import org.springframework.http.ResponseEntity;
+import org.springframework.validation.annotation.Validated;
+import org.springframework.web.bind.annotation.*;
+import org.springframework.web.context.request.NativeWebRequest;
+import org.springframework.web.multipart.MultipartFile;
+
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import jakarta.annotation.Generated;
+
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+@Validated
+@Tag(name = "visit", description = "Endpoints related to vet visits.")
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
+        description = "Creates a visit.",
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
+        description = "Returns the visit or a 404 error.",
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
+        @Min(0) @Parameter(name = "visitId", description = "The ID of the visit.", required = true, in = ParameterIn.PATH) @PathVariable("visitId") Integer visitId
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
+        description = "Returns the visit or a 404 error.",
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
+        @Min(0) @Parameter(name = "visitId", description = "The ID of the visit.", required = true, in = ParameterIn.PATH) @PathVariable("visitId") Integer visitId
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
+        description = "Returns an array of visit .",
+        tags = { "visit" },
+        responses = {
+            @ApiResponse(responseCode = "200", description = "visits found and returned.", content = {
+                @Content(mediaType = "application/json", array = @ArraySchema(schema = @Schema(implementation = VisitDto.class)))
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
+                    String exampleString = "[ null, null ]";
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
+        description = "Returns the visit or a 404 error.",
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
+        @Min(0) @Parameter(name = "visitId", description = "The ID of the visit.", required = true, in = ParameterIn.PATH) @PathVariable("visitId") Integer visitId,
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
@@ -0,0 +1,138 @@
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
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * OwnerAllOfDto
+ */
+
+@JsonTypeName("Owner_allOf")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class OwnerAllOfDto {
+
+  private Integer id;
+
+  @Valid
+  private List<@Valid PetDto> pets = new ArrayList<>();
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link OwnerAllOfDto#OwnerAllOfDto(List<@Valid PetDto>)}
+   */
+  @Deprecated
+  public OwnerAllOfDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public OwnerAllOfDto(List<@Valid PetDto> pets) {
+    this.pets = pets;
+  }
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
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet owner.", requiredMode = Schema.RequiredMode.NOT_REQUIRED)
+  @JsonProperty("id")
+  public Integer getId() {
+    return id;
+  }
+
+  public void setId(Integer id) {
+    this.id = id;
+  }
+
+  public OwnerAllOfDto pets(List<@Valid PetDto> pets) {
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
+  @Schema(name = "pets", accessMode = Schema.AccessMode.READ_ONLY, description = "The pets owned by this individual including any booked vet visits.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("pets")
+  public List<@Valid PetDto> getPets() {
+    return pets;
+  }
+
+  public void setPets(List<@Valid PetDto> pets) {
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
@@ -0,0 +1,264 @@
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
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * A pet owner.
+ */
+
+@Schema(name = "Owner", description = "A pet owner.")
+@JsonTypeName("Owner")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class OwnerDto {
+
+  private String firstName;
+
+  private String lastName;
+
+  private String address;
+
+  private String city;
+
+  private String telephone;
+
+  private Integer id;
+
+  @Valid
+  private List<@Valid PetDto> pets = new ArrayList<>();
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link OwnerDto#OwnerDto(String, String, String, String, String, List<@Valid PetDto>)}
+   */
+  @Deprecated
+  public OwnerDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public OwnerDto(String firstName, String lastName, String address, String city, String telephone, List<@Valid PetDto> pets) {
+    this.firstName = firstName;
+    this.lastName = lastName;
+    this.address = address;
+    this.city = city;
+    this.telephone = telephone;
+    this.pets = pets;
+  }
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
+  @Schema(name = "firstName", example = "George", description = "The first name of the pet owner.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("firstName")
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
+  @Schema(name = "lastName", example = "Franklin", description = "The last name of the pet owner.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("lastName")
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
+  @Schema(name = "address", example = "110 W. Liberty St.", description = "The postal address of the pet owner.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("address")
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
+  @Schema(name = "city", example = "Madison", description = "The city of the pet owner.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("city")
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
+  @Schema(name = "telephone", example = "6085551023", description = "The telephone number of the pet owner.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("telephone")
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
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet owner.", requiredMode = Schema.RequiredMode.NOT_REQUIRED)
+  @JsonProperty("id")
+  public Integer getId() {
+    return id;
+  }
+
+  public void setId(Integer id) {
+    this.id = id;
+  }
+
+  public OwnerDto pets(List<@Valid PetDto> pets) {
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
+  @Schema(name = "pets", accessMode = Schema.AccessMode.READ_ONLY, description = "The pets owned by this individual including any booked vet visits.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("pets")
+  public List<@Valid PetDto> getPets() {
+    return pets;
+  }
+
+  public void setPets(List<@Valid PetDto> pets) {
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
@@ -0,0 +1,202 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.OffsetDateTime;
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * Editable fields of a pet owner.
+ */
+
+@Schema(name = "OwnerFields", description = "Editable fields of a pet owner.")
+@JsonTypeName("OwnerFields")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class OwnerFieldsDto {
+
+  private String firstName;
+
+  private String lastName;
+
+  private String address;
+
+  private String city;
+
+  private String telephone;
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link OwnerFieldsDto#OwnerFieldsDto(String, String, String, String, String)}
+   */
+  @Deprecated
+  public OwnerFieldsDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public OwnerFieldsDto(String firstName, String lastName, String address, String city, String telephone) {
+    this.firstName = firstName;
+    this.lastName = lastName;
+    this.address = address;
+    this.city = city;
+    this.telephone = telephone;
+  }
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
+  @Schema(name = "firstName", example = "George", description = "The first name of the pet owner.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("firstName")
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
+  @Schema(name = "lastName", example = "Franklin", description = "The last name of the pet owner.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("lastName")
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
+  @Schema(name = "address", example = "110 W. Liberty St.", description = "The postal address of the pet owner.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("address")
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
+  @Schema(name = "city", example = "Madison", description = "The city of the pet owner.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("city")
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
+  @Schema(name = "telephone", example = "6085551023", description = "The telephone number of the pet owner.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("telephone")
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
@@ -0,0 +1,164 @@
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
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * PetAllOfDto
+ */
+
+@JsonTypeName("Pet_allOf")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class PetAllOfDto {
+
+  private Integer id;
+
+  private Integer ownerId;
+
+  @Valid
+  private List<@Valid VisitDto> visits = new ArrayList<>();
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link PetAllOfDto#PetAllOfDto(Integer, List<@Valid VisitDto>)}
+   */
+  @Deprecated
+  public PetAllOfDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public PetAllOfDto(Integer id, List<@Valid VisitDto> visits) {
+    this.id = id;
+    this.visits = visits;
+  }
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
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("id")
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
+  @Schema(name = "ownerId", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet's owner.", requiredMode = Schema.RequiredMode.NOT_REQUIRED)
+  @JsonProperty("ownerId")
+  public Integer getOwnerId() {
+    return ownerId;
+  }
+
+  public void setOwnerId(Integer ownerId) {
+    this.ownerId = ownerId;
+  }
+
+  public PetAllOfDto visits(List<@Valid VisitDto> visits) {
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
+  @Schema(name = "visits", accessMode = Schema.AccessMode.READ_ONLY, description = "Vet visit bookings for this pet.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("visits")
+  public List<@Valid VisitDto> getVisits() {
+    return visits;
+  }
+
+  public void setVisits(List<@Valid VisitDto> visits) {
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
@@ -0,0 +1,244 @@
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
+import org.springframework.samples.petclinic.rest.dto.PetTypeDto;
+import org.springframework.samples.petclinic.rest.dto.VisitDto;
+import java.time.OffsetDateTime;
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * A pet.
+ */
+
+@Schema(name = "Pet", description = "A pet.")
+@JsonTypeName("Pet")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class PetDto {
+
+  private String name;
+
+  @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
+  private LocalDate birthDate;
+
+  private PetTypeDto type;
+
+  private Integer id;
+
+  private Integer ownerId;
+
+  @Valid
+  private List<@Valid VisitDto> visits = new ArrayList<>();
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link PetDto#PetDto(String, LocalDate, PetTypeDto, Integer, List<@Valid VisitDto>)}
+   */
+  @Deprecated
+  public PetDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public PetDto(String name, LocalDate birthDate, PetTypeDto type, Integer id, List<@Valid VisitDto> visits) {
+    this.name = name;
+    this.birthDate = birthDate;
+    this.type = type;
+    this.id = id;
+    this.visits = visits;
+  }
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
+  @Schema(name = "name", example = "Leo", description = "The name of the pet.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("name")
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
+  @Schema(name = "birthDate", example = "Tue Sep 07 05:30:00 IST 2010", description = "The date of birth of the pet.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("birthDate")
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
+  @Schema(name = "type", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("type")
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
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("id")
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
+  @Schema(name = "ownerId", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet's owner.", requiredMode = Schema.RequiredMode.NOT_REQUIRED)
+  @JsonProperty("ownerId")
+  public Integer getOwnerId() {
+    return ownerId;
+  }
+
+  public void setOwnerId(Integer ownerId) {
+    this.ownerId = ownerId;
+  }
+
+  public PetDto visits(List<@Valid VisitDto> visits) {
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
+  @Schema(name = "visits", accessMode = Schema.AccessMode.READ_ONLY, description = "Vet visit bookings for this pet.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("visits")
+  public List<@Valid VisitDto> getVisits() {
+    return visits;
+  }
+
+  public void setVisits(List<@Valid VisitDto> visits) {
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
@@ -0,0 +1,156 @@
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
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * Editable fields of a pet.
+ */
+
+@Schema(name = "PetFields", description = "Editable fields of a pet.")
+@JsonTypeName("PetFields")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class PetFieldsDto {
+
+  private String name;
+
+  @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
+  private LocalDate birthDate;
+
+  private PetTypeDto type;
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link PetFieldsDto#PetFieldsDto(String, LocalDate, PetTypeDto)}
+   */
+  @Deprecated
+  public PetFieldsDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public PetFieldsDto(String name, LocalDate birthDate, PetTypeDto type) {
+    this.name = name;
+    this.birthDate = birthDate;
+    this.type = type;
+  }
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
+  @Schema(name = "name", example = "Leo", description = "The name of the pet.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("name")
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
+  @Schema(name = "birthDate", example = "Tue Sep 07 05:30:00 IST 2010", description = "The date of birth of the pet.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("birthDate")
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
+  @Schema(name = "type", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("type")
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
@@ -0,0 +1,102 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.OffsetDateTime;
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * PetTypeAllOfDto
+ */
+
+@JsonTypeName("PetType_allOf")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class PetTypeAllOfDto {
+
+  private Integer id;
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link PetTypeAllOfDto#PetTypeAllOfDto(Integer)}
+   */
+  @Deprecated
+  public PetTypeAllOfDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public PetTypeAllOfDto(Integer id) {
+    this.id = id;
+  }
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
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet type.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("id")
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
@@ -0,0 +1,128 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.OffsetDateTime;
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * A pet type.
+ */
+
+@Schema(name = "PetType", description = "A pet type.")
+@JsonTypeName("PetType")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class PetTypeDto {
+
+  private String name;
+
+  private Integer id;
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link PetTypeDto#PetTypeDto(String, Integer)}
+   */
+  @Deprecated
+  public PetTypeDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public PetTypeDto(String name, Integer id) {
+    this.name = name;
+    this.id = id;
+  }
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
+  @Schema(name = "name", example = "cat", description = "The name of the pet type.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("name")
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
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet type.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("id")
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
@@ -0,0 +1,102 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.OffsetDateTime;
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * Editable fields of a pet type.
+ */
+
+@Schema(name = "PetTypeFields", description = "Editable fields of a pet type.")
+@JsonTypeName("PetTypeFields")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class PetTypeFieldsDto {
+
+  private String name;
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link PetTypeFieldsDto#PetTypeFieldsDto(String)}
+   */
+  @Deprecated
+  public PetTypeFieldsDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public PetTypeFieldsDto(String name) {
+    this.name = name;
+  }
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
+  @Schema(name = "name", example = "cat", description = "The name of the pet type.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("name")
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
@@ -0,0 +1,267 @@
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
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * The schema for all error responses.
+ */
+
+@Schema(name = "RestError", description = "The schema for all error responses.")
+@JsonTypeName("RestError")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class RestErrorDto {
+
+  private Integer status;
+
+  private String error;
+
+  private URI path;
+
+  @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME)
+  private OffsetDateTime timestamp;
+
+  private String message;
+
+  @Valid
+  private List<ValidationMessageDto> schemaValidationErrors = new ArrayList<>();
+
+  private String trace;
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link RestErrorDto#RestErrorDto(Integer, String, URI, OffsetDateTime, String, List<ValidationMessageDto>)}
+   */
+  @Deprecated
+  public RestErrorDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public RestErrorDto(Integer status, String error, URI path, OffsetDateTime timestamp, String message, List<ValidationMessageDto> schemaValidationErrors) {
+    this.status = status;
+    this.error = error;
+    this.path = path;
+    this.timestamp = timestamp;
+    this.message = message;
+    this.schemaValidationErrors = schemaValidationErrors;
+  }
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
+  @Schema(name = "status", accessMode = Schema.AccessMode.READ_ONLY, example = "400", description = "The HTTP status code.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("status")
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
+  @Schema(name = "error", accessMode = Schema.AccessMode.READ_ONLY, example = "Bad Request", description = "The short error message.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("error")
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
+  @Schema(name = "path", accessMode = Schema.AccessMode.READ_ONLY, example = "/api/owners", description = "The path of the URL for this request.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("path")
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
+  @Schema(name = "timestamp", accessMode = Schema.AccessMode.READ_ONLY, description = "The time the error occured.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("timestamp")
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
+  @Schema(name = "message", accessMode = Schema.AccessMode.READ_ONLY, example = "Request failed schema validation", description = "The long error message.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("message")
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
+  @Schema(name = "schemaValidationErrors", description = "Validation errors against the OpenAPI schema.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("schemaValidationErrors")
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
+  @Schema(name = "trace", accessMode = Schema.AccessMode.READ_ONLY, example = "com.atlassian.oai.validator.springmvc.InvalidRequestException: ...", description = "The stacktrace for this error.", requiredMode = Schema.RequiredMode.NOT_REQUIRED)
+  @JsonProperty("trace")
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
@@ -0,0 +1,102 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.OffsetDateTime;
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * A role.
+ */
+
+@Schema(name = "Role", description = "A role.")
+@JsonTypeName("Role")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class RoleDto {
+
+  private String name;
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link RoleDto#RoleDto(String)}
+   */
+  @Deprecated
+  public RoleDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public RoleDto(String name) {
+    this.name = name;
+  }
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
+  @Schema(name = "name", example = "admin", description = "The role's name", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("name")
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
@@ -0,0 +1,128 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.OffsetDateTime;
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * Fields of specialty of vets.
+ */
+
+@Schema(name = "Specialty", description = "Fields of specialty of vets.")
+@JsonTypeName("Specialty")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class SpecialtyDto {
+
+  private Integer id;
+
+  private String name;
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link SpecialtyDto#SpecialtyDto(Integer, String)}
+   */
+  @Deprecated
+  public SpecialtyDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public SpecialtyDto(Integer id, String name) {
+    this.id = id;
+    this.name = name;
+  }
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
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the specialty.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("id")
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
+  @Schema(name = "name", example = "radiology", description = "The name of the specialty.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("name")
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
@@ -0,0 +1,186 @@
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
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * An user.
+ */
+
+@Schema(name = "User", description = "An user.")
+@JsonTypeName("User")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class UserDto {
+
+  private String username;
+
+  private String password;
+
+  private Boolean enabled;
+
+  @Valid
+  private List<@Valid RoleDto> roles;
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link UserDto#UserDto(String)}
+   */
+  @Deprecated
+  public UserDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public UserDto(String username) {
+    this.username = username;
+  }
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
+  @Schema(name = "username", example = "john.doe", description = "The username", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("username")
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
+  @Schema(name = "password", example = "1234", description = "The password", requiredMode = Schema.RequiredMode.NOT_REQUIRED)
+  @JsonProperty("password")
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
+  @Schema(name = "enabled", example = "true", description = "Indicates if the user is enabled", requiredMode = Schema.RequiredMode.NOT_REQUIRED)
+  @JsonProperty("enabled")
+  public Boolean getEnabled() {
+    return enabled;
+  }
+
+  public void setEnabled(Boolean enabled) {
+    this.enabled = enabled;
+  }
+
+  public UserDto roles(List<@Valid RoleDto> roles) {
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
+  @Schema(name = "roles", description = "The roles of an user", requiredMode = Schema.RequiredMode.NOT_REQUIRED)
+  @JsonProperty("roles")
+  public List<@Valid RoleDto> getRoles() {
+    return roles;
+  }
+
+  public void setRoles(List<@Valid RoleDto> roles) {
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
@@ -0,0 +1,107 @@
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
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * Messages describing a validation error.
+ */
+
+@Schema(name = "ValidationMessage", description = "Messages describing a validation error.")
+@JsonTypeName("ValidationMessage")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class ValidationMessageDto extends HashMap<String, Object> {
+
+  private String message;
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link ValidationMessageDto#ValidationMessageDto(String)}
+   */
+  @Deprecated
+  public ValidationMessageDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public ValidationMessageDto(String message) {
+    super();
+    this.message = message;
+  }
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
+  @Schema(name = "message", accessMode = Schema.AccessMode.READ_ONLY, example = "[Path '/lastName'] Instance type (null) does not match any allowed primitive type (allowed: [\"string\"])", description = "The valiation message.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("message")
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
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * VetAllOfDto
+ */
+
+@JsonTypeName("Vet_allOf")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class VetAllOfDto {
+
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
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the vet.", requiredMode = Schema.RequiredMode.NOT_REQUIRED)
+  @JsonProperty("id")
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
@@ -0,0 +1,190 @@
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
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * A veterinarian.
+ */
+
+@Schema(name = "Vet", description = "A veterinarian.")
+@JsonTypeName("Vet")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class VetDto {
+
+  private String firstName;
+
+  private String lastName;
+
+  @Valid
+  private List<@Valid SpecialtyDto> specialties = new ArrayList<>();
+
+  private Integer id;
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link VetDto#VetDto(String, String, List<@Valid SpecialtyDto>, Integer)}
+   */
+  @Deprecated
+  public VetDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public VetDto(String firstName, String lastName, List<@Valid SpecialtyDto> specialties, Integer id) {
+    this.firstName = firstName;
+    this.lastName = lastName;
+    this.specialties = specialties;
+    this.id = id;
+  }
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
+  @Schema(name = "firstName", example = "James", description = "The first name of the vet.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("firstName")
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
+  @Schema(name = "lastName", example = "Carter", description = "The last name of the vet.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("lastName")
+  public String getLastName() {
+    return lastName;
+  }
+
+  public void setLastName(String lastName) {
+    this.lastName = lastName;
+  }
+
+  public VetDto specialties(List<@Valid SpecialtyDto> specialties) {
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
+  @Schema(name = "specialties", description = "The specialties of the vet.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("specialties")
+  public List<@Valid SpecialtyDto> getSpecialties() {
+    return specialties;
+  }
+
+  public void setSpecialties(List<@Valid SpecialtyDto> specialties) {
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
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the vet.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("id")
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
@@ -0,0 +1,164 @@
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
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * Editable fields of a veterinarian.
+ */
+
+@Schema(name = "VetFields", description = "Editable fields of a veterinarian.")
+@JsonTypeName("VetFields")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class VetFieldsDto {
+
+  private String firstName;
+
+  private String lastName;
+
+  @Valid
+  private List<@Valid SpecialtyDto> specialties = new ArrayList<>();
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link VetFieldsDto#VetFieldsDto(String, String, List<@Valid SpecialtyDto>)}
+   */
+  @Deprecated
+  public VetFieldsDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public VetFieldsDto(String firstName, String lastName, List<@Valid SpecialtyDto> specialties) {
+    this.firstName = firstName;
+    this.lastName = lastName;
+    this.specialties = specialties;
+  }
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
+  @Schema(name = "firstName", example = "James", description = "The first name of the vet.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("firstName")
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
+  @Schema(name = "lastName", example = "Carter", description = "The last name of the vet.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("lastName")
+  public String getLastName() {
+    return lastName;
+  }
+
+  public void setLastName(String lastName) {
+    this.lastName = lastName;
+  }
+
+  public VetFieldsDto specialties(List<@Valid SpecialtyDto> specialties) {
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
+  @Schema(name = "specialties", description = "The specialties of the vet.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("specialties")
+  public List<@Valid SpecialtyDto> getSpecialties() {
+    return specialties;
+  }
+
+  public void setSpecialties(List<@Valid SpecialtyDto> specialties) {
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
@@ -0,0 +1,127 @@
+package org.springframework.samples.petclinic.rest.dto;
+
+import java.net.URI;
+import java.util.Objects;
+import com.fasterxml.jackson.annotation.JsonProperty;
+import com.fasterxml.jackson.annotation.JsonCreator;
+import com.fasterxml.jackson.annotation.JsonTypeName;
+import java.time.OffsetDateTime;
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * VisitAllOfDto
+ */
+
+@JsonTypeName("Visit_allOf")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class VisitAllOfDto {
+
+  private Integer id;
+
+  private Integer petId;
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link VisitAllOfDto#VisitAllOfDto(Integer)}
+   */
+  @Deprecated
+  public VisitAllOfDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public VisitAllOfDto(Integer id) {
+    this.id = id;
+  }
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
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the visit.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("id")
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
+  @Schema(name = "petId", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet.", requiredMode = Schema.RequiredMode.NOT_REQUIRED)
+  @JsonProperty("petId")
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
@@ -0,0 +1,180 @@
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
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * A booking for a vet visit.
+ */
+
+@Schema(name = "Visit", description = "A booking for a vet visit.")
+@JsonTypeName("Visit")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class VisitDto {
+
+  @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
+  private LocalDate date;
+
+  private String description;
+
+  private Integer id;
+
+  private Integer petId;
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link VisitDto#VisitDto(String, Integer)}
+   */
+  @Deprecated
+  public VisitDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public VisitDto(String description, Integer id) {
+    this.description = description;
+    this.id = id;
+  }
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
+  @Schema(name = "date", example = "Tue Jan 01 05:30:00 IST 2013", description = "The date of the visit.", requiredMode = Schema.RequiredMode.NOT_REQUIRED)
+  @JsonProperty("date")
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
+  @Schema(name = "description", example = "rabies shot", description = "The description for the visit.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("description")
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
+  @Schema(name = "id", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the visit.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("id")
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
+  @Schema(name = "petId", accessMode = Schema.AccessMode.READ_ONLY, example = "1", description = "The ID of the pet.", requiredMode = Schema.RequiredMode.NOT_REQUIRED)
+  @JsonProperty("petId")
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
@@ -0,0 +1,129 @@
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
+import jakarta.validation.Valid;
+import jakarta.validation.constraints.*;
+import org.hibernate.validator.constraints.*;
+import io.swagger.v3.oas.annotations.media.Schema;
+
+
+import java.util.*;
+import jakarta.annotation.Generated;
+
+/**
+ * Editable fields of a vet visit.
+ */
+
+@Schema(name = "VisitFields", description = "Editable fields of a vet visit.")
+@JsonTypeName("VisitFields")
+@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2026-10-22T18:49:00.409018+05:30[Asia/Kolkata]")
+public class VisitFieldsDto {
+
+  @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
+  private LocalDate date;
+
+  private String description;
+
+  /**
+   * Default constructor
+   * @deprecated Use {@link VisitFieldsDto#VisitFieldsDto(String)}
+   */
+  @Deprecated
+  public VisitFieldsDto() {
+    super();
+  }
+
+  /**
+   * Constructor with only required parameters
+   */
+  public VisitFieldsDto(String description) {
+    this.description = description;
+  }
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
+  @Schema(name = "date", example = "Tue Jan 01 05:30:00 IST 2013", description = "The date of the visit.", requiredMode = Schema.RequiredMode.NOT_REQUIRED)
+  @JsonProperty("date")
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
+  @Schema(name = "description", example = "rabies shot", description = "The description for the visit.", requiredMode = Schema.RequiredMode.REQUIRED)
+  @JsonProperty("description")
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

The most likely issue is that the upgrade to Spring Boot 3 has introduced breaking changes in Hibernate, which is used for database operations. Specifically, the error messages indicate that Hibernate is unable to interpret path expressions like 'pet_id' and 'type_id'. The developer should first check the entity classes to ensure that the field names and relationships are correctly defined. They should also verify that any custom queries or JPQL/HQL statements are updated to be compatible with Hibernate 3. Additionally, checking for any deprecated or removed methods or annotations in Spring Data JPA could help identify other potential issues.

## Last build error (best state)
```
[ERROR] Tests run: 33, Failures: 0, Errors: 2, Skipped: 0, Time elapsed: 0.677 s <<< FAILURE! -- in org.springframework.samples.petclinic.service.clinicService.ClinicServiceJpaTests
[ERROR] org.springframework.samples.petclinic.service.clinicService.ClinicServiceJpaTests.shouldDeletePet -- Time elapsed: 0.008 s <<< ERROR!
Caused by: java.lang.IllegalArgumentException: org.hibernate.query.SemanticException: Could not interpret path expression 'pet_id'
Caused by: org.hibernate.query.SemanticException: Could not interpret path expression 'pet_id'
[ERROR] org.springframework.samples.petclinic.service.clinicService.ClinicServiceJpaTests.shouldDeletePetType -- Time elapsed: 0.004 s <<< ERROR!
Caused by: java.lang.IllegalArgumentException: org.hibernate.query.SemanticException: Could not interpret path expression 'type_id'
Caused by: org.hibernate.query.SemanticException: Could not interpret path expression 'type_id'
[ERROR] Errors: 
[ERROR]   ClinicServiceJpaTests>AbstractClinicServiceTests.shouldDeletePet:213 » InvalidDataAccessApiUsage org.hibernate.query.SemanticException: Could not interpret path expression 'pet_id'
[ERROR]   ClinicServiceJpaTests>AbstractClinicServiceTests.shouldDeletePetType:402 » InvalidDataAccessApiUsage org.hibernate.query.SemanticException: Could not interpret path expression 'type_id'
[ERROR] Tests run: 172, Failures: 0, Errors: 2, Skipped: 0
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.2.5:test (default-test) on project spring-petclinic-rest: 
[ERROR] 
[ERROR] Please refer to /private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-out/migrated-spring-petclinic-rest/target/surefire-reports for the individual test results.
[ERROR] Please refer to dump files (if any exist) [date].dump, [date]-jvmRun[N].dump and [date].dumpstream.
[ERROR] -> [Help 1]
[ERROR] 
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR] 
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
```