# Project: Spring Boot + Thymeleaf

This application implements the project as a Spring Boot monolith that renders its user interface directly on the server side using Thymeleaf. All user input is validated using Jakarta Bean Validation, and any errors are displayed directly in the form with field-specific messages.

## Let's get started

Prerequisites: **Java 21** and **Gradle**

```bash
./gradlew clean bootRun
```

The app launches at **http://localhost:8080** and automatically creates two demo patients (only on the very first launch; see `DemoDataSeeder`).

- Patient list: `/patients`
- H2 console (to view the database): `/h2-console` (JDBC URL: `jdbc:h2:file:./medic-db`, username `sa`, no password)
- Uploaded files are stored in `./uploads/` and served via `/media/**`.

## Important note on X-ray image analysis

The `MlAnalysisService` interface is designed to be interchangeable; it can be switched via `ml.analysis.provider` in `application.properties`:

- **`simulated`:** `SimulatedMlAnalysisService` — generates deterministic probabilities for the 14 NIH ChestX-ray14 pathologies, as well as an overlay image that is visually modelled on Grad-CAM but is entirely synthetic. **These results are not medically actionable** and are consistently marked with a warning in the UI. Runs without external dependencies.
- **`rest` (default):** `RestMlAnalysisService` — calls the actual PyTorch/DenseNet model code via a small FastAPI microservice at `/ml-service`. Setup and details can be found in `ml-service/README.md`. For this to work, the FastAPI server must be running. Information on this is described in the [server’s README](./ml-service/README.md).

## Production operation

To switch from H2 to Postgres/MySQL: include the appropriate JDBC driver in `gradlew` and adjust `spring.datasource.*` in `application.properties` (or via an environment variable).

## Tests

For Spring Boot:

```bash
./gradlew test
```

For FastAPI:
```bash
source .venv/bin/activate
pip install -r .\requirements-test.txt
pytest
```
