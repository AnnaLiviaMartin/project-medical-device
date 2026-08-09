# MedIC Chart — Spring Boot + Thymeleaf

Diese Anwendung ist die neu gedachte Architektur des urspruenglichen Projekts:
statt eines Django-REST-Backends (drei Apps: `patients`, `imaging`, `ml`) mit
separatem Next.js-Frontend ist alles jetzt **ein einziger Spring-Boot-
Monolith**, der seine Oberflaeche direkt serverseitig mit **Thymeleaf**
rendert. Jede Nutzereingabe (neuer Patient, Historieneintrag, Datei-Upload)
laeuft durch **Jakarta Bean Validation** und wird bei Fehlern mit
feldgenauen Meldungen direkt im Formular angezeigt.

## Warum diese Architektur?

| Vorher (Django + Next.js)                                   | Jetzt (Spring Boot + Thymeleaf)                                  |
|---------------------------------------------------------------|--------------------------------------------------------------------|
| 3 Django-Apps (`patients`, `imaging`, `ml`) + DRF-Serializer   | 1 Modul, klar getrennt in `domain` / `repository` / `service` / `controller` |
| Separates Next.js-Frontend, konsumiert JSON ueber REST         | Server-gerenderte Thymeleaf-Views, kein zweites Deployment, kein CORS |
| Validierung teils nur im Frontend (`NewPatientForm.tsx`)       | Validierung zentral & serverseitig über `@Valid` + Bean-Validation-Annotationen auf den Formular-DTOs |
| PyTorch/DenseNet-Modell + Grad-CAM (Python-spezifisch)         | Austauschbare `MlAnalysisService`-Schnittstelle, aktuell mit klar gekennzeichneter Simulation gefuellt |
| SQLite/Postgres via Django ORM                                 | H2 (dateibasiert, laeuft ohne Setup) via Spring Data JPA, per Property auf Postgres/MySQL umstellbar |

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

Das ursprüngliche PyTorch/DenseNet-Modell mit Grad-CAM lässt sich nicht 1:1
nach Java portieren. Die Schnittstelle `MlAnalysisService` ist deshalb
bewusst austauschbar gehalten:

- **Aktuell aktiv:** `SimulatedMlAnalysisService` — erzeugt plausible,
  deterministische (per Bild-Hash geseedete) Wahrscheinlichkeiten für die
  14 NIH-ChestX-ray14-Pathologien sowie ein optisch an Grad-CAM angelehntes,
  aber komplett synthetisches Overlay-Bild. **Diese Ergebnisse sind nicht
  medizinisch verwertbar** und werden in der UI durchgängig mit einem
  Warnhinweis gekennzeichnet.
- **Für eine echte Anbindung** böten sich an, jeweils hinter derselben
  Schnittstelle, ohne Änderungen an Controller/Service-Schicht:
  1. Das Modell bleibt in Python, läuft als eigener kleiner
     Inferenz-Microservice (z. B. FastAPI); `RestMlAnalysisService` ruft
     ihn per `RestClient`/`WebClient` auf.
  2. Modell nach ONNX/TorchScript exportieren und über
     [Deep Java Library](https://djl.ai) direkt in der JVM ausführen.

## Produktivbetrieb

Für den Wechsel von H2 auf Postgres/MySQL: den passenden JDBC-Treiber in
die `pom.xml` aufnehmen und `spring.datasource.*` in
`application.properties` (oder per Umgebungsvariable) anpassen — der Rest
der Anwendung bleibt unverändert, da ausschließlich über Spring Data JPA
zugegriffen wird.
