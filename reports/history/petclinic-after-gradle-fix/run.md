# Migration report

- App: `spring-petclinic`  |  Model: `qwen2.5-coder:7b-instruct`  |  Upgrade tool: OpenRewrite (rewrite-spring 6.37.1)
- Spring Boot parent after upgrade: `3.3.13`
- Gradle files ignored in the work copy (the agent is Maven-only): build.gradle, settings.gradle, gradlew, gradlew.bat, gradle/
- Result: **tests PASS**
- Model fix rounds: 0 (max 5)
- Settings: temperature 0, seed 0, 8192-token context; output fingerprint `cfec0e9efd74` (identical fingerprints across runs mean identical generated code)

## Build score per run

Score = failing tests, or 1000+ compile errors. 0 means green. A run that scores worse than the best so far is rolled back.

| Run | Score | Tests passed | What happened |
|---|---|---|---|
| 1 | 0 | all | build |

## Test integrity

- Existing files under `src/test` (tests and test resources) and every `pom.xml` / `.mvn` file are hashed after the upgrade tool runs and again at the end. The fix loop can only write under `src/main`.
- The upgraded pom must not gain test-skipping settings (`skipTests`, `maven.test.skip`, `testFailureIgnore`, surefire `skip` or excludes).
- A passing run must execute exactly the baseline's tests: the original app ran 41 tests, 40 passed.
- Result: no violations.

The upgrade tool itself (not the model) rewrote these test files: `src/test/java/org/springframework/samples/petclinic/model/ValidatorTests.java`

## Security equivalence (same requests, Boot 2 build vs upgraded build)

10 checks, **0 difference(s)**, of which **0 newly accessible**. Cells show the HTTP status; changed cells show before → after. 401/403 means denied; 404 means the route was not found, which is a different problem.

| Endpoint | anonymous |
|---|---|
| `GET /` | 200 |
| `GET /actuator/health` | 200 |
| `GET /oups` | 500 |
| `GET /owners/1` | 200 |
| `GET /owners/1/edit` | 200 |
| `GET /owners/1/pets/new` | 200 |
| `GET /owners/find` | 200 |
| `GET /owners?lastName=Davis` | 200 |
| `GET /vets` | 200 |
| `GET /vets.html` | 200 |

## Diff (all changes to Java sources, including the upgrade tool's)
```diff
--- a/BaseEntity.java
+++ b/BaseEntity.java
@@ -17,10 +17,10 @@
 
 import java.io.Serializable;
 
-import javax.persistence.GeneratedValue;
-import javax.persistence.GenerationType;
-import javax.persistence.Id;
-import javax.persistence.MappedSuperclass;
+import jakarta.persistence.GeneratedValue;
+import jakarta.persistence.GenerationType;
+import jakarta.persistence.Id;
+import jakarta.persistence.MappedSuperclass;
 
 /**
  * Simple JavaBean domain object with an id property. Used as a base class for objects

--- a/NamedEntity.java
+++ b/NamedEntity.java
@@ -15,8 +15,8 @@
  */
 package org.springframework.samples.petclinic.model;
 
-import javax.persistence.Column;
-import javax.persistence.MappedSuperclass;
+import jakarta.persistence.Column;
+import jakarta.persistence.MappedSuperclass;
 
 /**
  * Simple JavaBean domain object adds a name property to <code>BaseEntity</code>. Used as

--- a/Person.java
+++ b/Person.java
@@ -15,9 +15,9 @@
  */
 package org.springframework.samples.petclinic.model;
 
-import javax.persistence.Column;
-import javax.persistence.MappedSuperclass;
-import javax.validation.constraints.NotEmpty;
+import jakarta.persistence.Column;
+import jakarta.persistence.MappedSuperclass;
+import jakarta.validation.constraints.NotEmpty;
 
 /**
  * Simple JavaBean domain object representing an person.

--- a/Owner.java
+++ b/Owner.java
@@ -18,16 +18,16 @@
 import java.util.ArrayList;
 import java.util.List;
 
-import javax.persistence.CascadeType;
-import javax.persistence.Column;
-import javax.persistence.Entity;
-import javax.persistence.FetchType;
-import javax.persistence.JoinColumn;
-import javax.persistence.OneToMany;
-import javax.persistence.OrderBy;
-import javax.persistence.Table;
-import javax.validation.constraints.Digits;
-import javax.validation.constraints.NotEmpty;
+import jakarta.persistence.CascadeType;
+import jakarta.persistence.Column;
+import jakarta.persistence.Entity;
+import jakarta.persistence.FetchType;
+import jakarta.persistence.JoinColumn;
+import jakarta.persistence.OneToMany;
+import jakarta.persistence.OrderBy;
+import jakarta.persistence.Table;
+import jakarta.validation.constraints.Digits;
+import jakarta.validation.constraints.NotEmpty;
 
 import org.springframework.core.style.ToStringCreator;
 import org.springframework.samples.petclinic.model.Person;

--- a/OwnerController.java
+++ b/OwnerController.java
@@ -17,7 +17,7 @@
 
 import java.util.List;
 import java.util.Map;
-import javax.validation.Valid;
+import jakarta.validation.Valid;
 import org.springframework.data.domain.Page;
 import org.springframework.data.domain.PageRequest;
 import org.springframework.data.domain.Pageable;

--- a/Pet.java
+++ b/Pet.java
@@ -20,15 +20,15 @@
 import java.util.LinkedHashSet;
 import java.util.Set;
 
-import javax.persistence.CascadeType;
-import javax.persistence.Column;
-import javax.persistence.Entity;
-import javax.persistence.FetchType;
-import javax.persistence.JoinColumn;
-import javax.persistence.ManyToOne;
-import javax.persistence.OneToMany;
-import javax.persistence.OrderBy;
-import javax.persistence.Table;
+import jakarta.persistence.CascadeType;
+import jakarta.persistence.Column;
+import jakarta.persistence.Entity;
+import jakarta.persistence.FetchType;
+import jakarta.persistence.JoinColumn;
+import jakarta.persistence.ManyToOne;
+import jakarta.persistence.OneToMany;
+import jakarta.persistence.OrderBy;
+import jakarta.persistence.Table;
 
 import org.springframework.format.annotation.DateTimeFormat;
 import org.springframework.samples.petclinic.model.NamedEntity;

--- a/PetController.java
+++ b/PetController.java
@@ -16,7 +16,7 @@
 package org.springframework.samples.petclinic.owner;
 
 import java.util.Collection;
-import javax.validation.Valid;
+import jakarta.validation.Valid;
 import org.springframework.stereotype.Controller;
 import org.springframework.ui.ModelMap;
 import org.springframework.util.StringUtils;

--- a/PetType.java
+++ b/PetType.java
@@ -15,8 +15,8 @@
  */
 package org.springframework.samples.petclinic.owner;
 
-import javax.persistence.Entity;
-import javax.persistence.Table;
+import jakarta.persistence.Entity;
+import jakarta.persistence.Table;
 
 import org.springframework.samples.petclinic.model.NamedEntity;
 

--- a/PetTypeFormatter.java
+++ b/PetTypeFormatter.java
@@ -15,7 +15,6 @@
  */
 package org.springframework.samples.petclinic.owner;
 
-import org.springframework.beans.factory.annotation.Autowired;
 import org.springframework.format.Formatter;
 import org.springframework.stereotype.Component;
 
@@ -38,7 +37,6 @@
 
 	private final OwnerRepository owners;
 
-	@Autowired
 	public PetTypeFormatter(OwnerRepository owners) {
 		this.owners = owners;
 	}

--- a/Visit.java
+++ b/Visit.java
@@ -17,10 +17,10 @@
 
 import java.time.LocalDate;
 
-import javax.persistence.Column;
-import javax.persistence.Entity;
-import javax.persistence.Table;
-import javax.validation.constraints.NotEmpty;
+import jakarta.persistence.Column;
+import jakarta.persistence.Entity;
+import jakarta.persistence.Table;
+import jakarta.validation.constraints.NotEmpty;
 
 import org.springframework.format.annotation.DateTimeFormat;
 import org.springframework.samples.petclinic.model.BaseEntity;

--- a/VisitController.java
+++ b/VisitController.java
@@ -17,7 +17,7 @@
 
 import java.util.Map;
 
-import javax.validation.Valid;
+import jakarta.validation.Valid;
 
 import org.springframework.stereotype.Controller;
 import org.springframework.validation.BindingResult;

--- a/Specialty.java
+++ b/Specialty.java
@@ -15,8 +15,8 @@
  */
 package org.springframework.samples.petclinic.vet;
 
-import javax.persistence.Entity;
-import javax.persistence.Table;
+import jakarta.persistence.Entity;
+import jakarta.persistence.Table;
 
 import org.springframework.samples.petclinic.model.NamedEntity;
 

--- a/Vet.java
+++ b/Vet.java
@@ -21,13 +21,13 @@
 import java.util.List;
 import java.util.Set;
 
-import javax.persistence.Entity;
-import javax.persistence.FetchType;
-import javax.persistence.JoinColumn;
-import javax.persistence.JoinTable;
-import javax.persistence.ManyToMany;
-import javax.persistence.Table;
-import javax.xml.bind.annotation.XmlElement;
+import jakarta.persistence.Entity;
+import jakarta.persistence.FetchType;
+import jakarta.persistence.JoinColumn;
+import jakarta.persistence.JoinTable;
+import jakarta.persistence.ManyToMany;
+import jakarta.persistence.Table;
+import jakarta.xml.bind.annotation.XmlElement;
 
 import org.springframework.beans.support.MutableSortDefinition;
 import org.springframework.beans.support.PropertyComparator;

--- a/Vets.java
+++ b/Vets.java
@@ -15,8 +15,8 @@
  */
 package org.springframework.samples.petclinic.vet;
 
-import javax.xml.bind.annotation.XmlElement;
-import javax.xml.bind.annotation.XmlRootElement;
+import jakarta.xml.bind.annotation.XmlElement;
+import jakarta.xml.bind.annotation.XmlRootElement;
 import java.util.ArrayList;
 import java.util.List;
 

--- a/ValidatorTests.java
+++ b/ValidatorTests.java
@@ -20,8 +20,8 @@
 import org.springframework.context.i18n.LocaleContextHolder;
 import org.springframework.validation.beanvalidation.LocalValidatorFactoryBean;
 
-import javax.validation.ConstraintViolation;
-import javax.validation.Validator;
+import jakarta.validation.ConstraintViolation;
+import jakarta.validation.Validator;
 import java.util.Locale;
 import java.util.Set;
 

```