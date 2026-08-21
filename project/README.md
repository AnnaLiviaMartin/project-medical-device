# MedIC Chart — Spring Boot + Thymeleaf

Diese Anwendung ist die neu gedachte Architektur des urspruenglichen Projekts: statt eines Django-REST-Backends (drei Apps: `patients`, `imaging`, `ml`) mit separatem Next.js-Frontend ist alles jetzt **ein einziger Spring-Boot-Monolith**, der seine Oberflaeche direkt serverseitig mit **Thymeleaf** rendert. Jede Nutzereingabe (neuer Patient, Historieneintrag, Datei-Upload laeuft durch **Jakarta Bean Validation** und wird bei Fehlern mit feldgenauen Meldungen direkt im Formular angezeigt.

## Los geht's

Voraussetzungen: **Java 21** und **Gradle**

```bash
./gradlew clean bootRun
```

Die App startet auf **http://localhost:8080** und legt automatisch zwei
Demo-Patienten an (nur beim allerersten Start, siehe `DemoDataSeeder`).

- Patientenliste: `/patients`
- H2-Konsole (zum Reinschauen in die Datenbank): `/h2-console`
  (JDBC-URL: `jdbc:h2:file:./medic-db`, User `sa`, kein Passwort)
- Hochgeladene Dateien landen unter `./uploads/` und werden über `/media/**`
  ausgeliefert.

## Wichtiger Hinweis zur Röntgenbild-Analyse

Die Schnittstelle `MlAnalysisService` ist austauschbar gehalten, umschaltbar über `ml.analysis.provider` in `application.properties`:

- **`simulated` (Standard):** `SimulatedMlAnalysisService` — erzeugt plausible, deterministische (per Bild-Hash geseedete) Wahrscheinlichkeiten für die 14 NIH-ChestX-ray14-Pathologien sowie ein optisch an Grad-CAM angelehntes, aber komplett synthetisches Overlay-Bild. **Diese Ergebnisse sind nicht medizinisch verwertbar** und werden in der UI durchgängig mit einem Warnhinweis gekennzeichnet. Läuft ohne externe Abhängigkeiten.
- **`rest`:** `RestMlAnalysisService` — ruft den echten PyTorch/DenseNet-Model-Code über einen kleinen FastAPI-Microservice unter `/ml-service` auf. Setup und Details dort in `ml-service/README.md`.

## Produktivbetrieb

Für den Wechsel von H2 auf Postgres/MySQL: den passenden JDBC-Treiber in die `pom.xml` aufnehmen und `spring.datasource.*` in `application.properties` (oder per Umgebungsvariable) anpassen — der Rest der Anwendung bleibt unverändert, da ausschließlich über Spring Data JPA zugegriffen wird.

## Tests

Für Spring Boot:

```bash
./gradlew test
```

Für FastAPI:
```bash
source .venv/bin/activate
pip install -r .\requirements-test.txt
pytest
```
