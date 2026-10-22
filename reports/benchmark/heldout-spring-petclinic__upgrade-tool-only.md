# Migration report

- App: `spring-petclinic`  |  Model: none (upgrade tool only)  |  Upgrade tool: built-in fallback
- Spring Boot parent after upgrade: `3.3.5`
- **Warning: the built-in fallback was used, not OpenRewrite.** OpenRewrite failed: [ERROR] Failed to execute goal org.openrewrite.maven:rewrite-maven-plugin:6.46.1:run (default-cli) on project spring-petclinic: Execution default-cli of goal org.openrewrite.maven:rewrite-maven-plugin:6.46.1:run failed: Failed to download https://downloads.gradle.org/distributions/gradle-7.6.6-bin.zip to artifact cache -> [Help 1] | [ERROR]  | [ERROR] To see the full stack trace of the errors, re-run 
- Result: **NEEDS HUMAN REVIEW (tests failing)**
- Model fix rounds: 0 (max 0)
- Settings: temperature 0, seed 0, 8192-token context; output fingerprint `924d0578148d` (identical fingerprints across runs mean identical generated code)

## Build score per run

Score = failing tests, or 1000+ compile errors. 0 means green. A run that scores worse than the best so far is rolled back.

| Run | Score | Tests passed | What happened |
|---|---|---|---|
| 1 | 500 | - | build |

## Test integrity

- Existing files under `src/test` (tests and test resources) and every `pom.xml` / `.mvn` file are hashed after the upgrade tool runs and again at the end. The fix loop can only write under `src/main`.
- The upgraded pom must not gain test-skipping settings (`skipTests`, `maven.test.skip`, `testFailureIgnore`, surefire `skip` or excludes).
- A passing run must execute exactly the baseline's tests: the original app ran 41 tests, 40 passed.
- Result: no violations.

The upgrade tool itself (not the model) rewrote these test files: `src/test/java/org/springframework/samples/petclinic/model/ValidatorTests.java`

## Security equivalence

Could not run:
```
app did not start:
[ERROR] [ERROR] Some problems were encountered while processing the POMs:
[WARNING] 'build.plugins.plugin.version' for pl.project13.maven:git-commit-id-plugin is missing. @ line 203, column 15
[ERROR] 'dependencies.dependency.version' for mysql:mysql-connector-java:jar is missing. @ line 70, column 17
 @ 
[ERROR] The build could not read 1 project -> [Help 1]
[ERROR]   
[ERROR]   The project org.springframework.samples:spring-petclinic:2.7.3 (/private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-bench/migrated-heldout-spring-petclinic__upgrade-tool-only/pom.xml) has 1 error
[ERROR]     'dependencies.dependency.version' for mysql:mysql-connector-java:jar is missing. @ line 70, column 17
[ERROR] 
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR] 
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/ProjectBuildingException
```

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
@@ -21,12 +21,12 @@
 import java.util.List;
 import java.util.Set;
 
-import javax.persistence.Entity;
-import javax.persistence.FetchType;
-import javax.persistence.JoinColumn;
-import javax.persistence.JoinTable;
-import javax.persistence.ManyToMany;
-import javax.persistence.Table;
+import jakarta.persistence.Entity;
+import jakarta.persistence.FetchType;
+import jakarta.persistence.JoinColumn;
+import jakarta.persistence.JoinTable;
+import jakarta.persistence.ManyToMany;
+import jakarta.persistence.Table;
 import javax.xml.bind.annotation.XmlElement;
 
 import org.springframework.beans.support.MutableSortDefinition;

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

## Last build error (best state)
```
[ERROR] [ERROR] Some problems were encountered while processing the POMs:
[ERROR] 'dependencies.dependency.version' for mysql:mysql-connector-java:jar is missing. @ line 70, column 17
[ERROR] The build could not read 1 project -> [Help 1]
[ERROR]   
[ERROR]   The project org.springframework.samples:spring-petclinic:2.7.3 (/private/var/folders/n1/80srjmy90vlc981g_j9ychzc0000gn/T/boot-upgrade-bench/migrated-heldout-spring-petclinic__upgrade-tool-only/pom.xml) has 1 error
[ERROR]     'dependencies.dependency.version' for mysql:mysql-connector-java:jar is missing. @ line 70, column 17
[ERROR] 
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR] 
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/ProjectBuildingException
```