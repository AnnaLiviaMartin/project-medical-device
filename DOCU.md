# Documentation of developing process

This documentation describes any additional information we want to provide you (the reader) about our project. This mainly includes a description our descisions regarding the machine learning model and the development of our application.

## Machine Learning

### Machine-Learning-Modell

Die Machine-Learning-Komponente wurde in Anlehnung an die Architektur- und Modellierungsentscheidungen von CheXNet von Rajpurkar et al. [1] entwickelt. Ziel war die Erkennung von Auffälligkeiten in Röntgenaufnahmen des Brustkorbs.

Als Grundlage wurde ein auf ImageNet vortrainiertes DenseNet-121 verwendet und auf dem NIH Chest X-ray Dataset weitertrainiert. Die Architektur wurde dabei an die Anforderungen des entwickelten Prototyps angepasst.

### Datengrundlage und Datenaufteilung

Als Datengrundlage diente das NIH Chest X-ray Dataset mit 112.120 Röntgenaufnahmen von 30.805 Patienten und 14 thorakalen Pathologien [2].

Für die Aufteilung wurden die offiziellen Train- und Test-Listen des Datensatzes verwendet. Zusätzlich wurde aus den Trainingsdaten ein separater Validierungsdatensatz erstellt. Die Aufteilung erfolgte auf Patientenebene, sodass Aufnahmen eines Patienten nicht gleichzeitig in Trainings-, Validierungs- und Testdaten vorkommen.

Um dies technisch abzusichern, wurden drei Überschneidungsprüfungen zwischen Trainings-, Validierungs- und Testdaten implementiert und über Assertions abgesichert. Dadurch wird verhindert, dass Daten desselben Patienten versehentlich in mehreren Datensätzen verwendet werden.

Modellarchitektur und Klassifikationsaufgabe

Als Modell wurde DenseNet-121 gewählt, da diese Architektur auch in CheXNet für den NIH Chest X-ray Dataset verwendet wird [1].

Der ursprüngliche Klassifikationskopf des vortrainierten Modells wurde durch einen eigenen Klassifikationskopf mit 14 Ausgabeneuronen ersetzt. Jede Ausgabe entspricht einer der 14 Pathologien des Datensatzes. Da mehrere Pathologien gleichzeitig auftreten können, wurde die Aufgabe als Multi-Label-Klassifikation umgesetzt.

Der Klassifikationskopf enthält zusätzlich eine Dropout-Schicht mit $p=0.25$. Das Modell gibt zunächst Logits aus, die bei der Inferenz mithilfe der Sigmoid-Funktion in Wahrscheinlichkeiten zwischen 0 und 1 umgewandelt werden.

No Finding wurde nicht als eigene Ausgabeklasse modelliert. Der Zustand wird implizit angenommen, wenn keine der 14 Pathologien den jeweiligen Klassifikationsschwellenwert überschreitet.

### Trainingsverfahren

Das Training wurde in zwei Phasen umgesetzt. Zunächst wurden die trainierbaren Parameter auf den neu hinzugefügten Klassifikationskopf beschränkt. Anschließend wurde der Backbone für das Fine-Tuning freigegeben und mit einer niedrigeren Lernrate weitertrainiert.

Als Verlustfunktion wurde BCEWithLogitsLoss verwendet. Diese eignet sich für die verwendete Multi-Label-Klassifikation und kombiniert die Sigmoid-Funktion mit der binären Kreuzentropie in einer numerisch stabilen Form.

Da die Pathologien unterschiedlich häufig im Trainingsdatensatz vorkommen, wurden klassenabhängige pos_weight-Werte verwendet. Diese wurden aus der Klassenverteilung des Trainingsdatensatzes abgeleitet. Zur Begrenzung der Gewichtung sehr seltener Klassen wurden die Werte zusätzlich mittels Quadratwurzel-Dämpfung angepasst.

Modellauswahl und Evaluation

Für die Auswahl des besten Modellzustands wurde die Macro-AUC auf dem Validierungsdatensatz verwendet. Dabei werden die ROC-AUC-Werte der einzelnen 14 Pathologien gemittelt, sodass jede Klasse unabhängig von ihrer Häufigkeit gleich berücksichtigt wird.

Das beste beobachtete Ergebnis auf dem Validierungsdatensatz betrug:

Validation Macro-AUC: 0.8354

Für die einzelnen Pathologien wurden anschließend Klassifikationsschwellen mithilfe des Youden-Index auf dem Validierungsdatensatz bestimmt. Die ermittelten Schwellenwerte wurden unverändert auf den Testdatensatz angewendet. Die Testdaten wurden somit nicht zur Optimierung der Schwellenwerte verwendet.

Erklärbarkeit und Integration

Die vom Modell berechneten Wahrscheinlichkeiten werden im Prototyp zur Darstellung der erkannten Pathologien verwendet. Zusätzlich wird Grad-CAM eingesetzt, um relevante Bildbereiche für eine Modellvorhersage hervorzuheben [3].

Die Grad-CAM-Darstellung dient dabei als zusätzliche Information zur Nachvollziehbarkeit der Modellentscheidung und stellt keine eigenständige medizinische Diagnose dar.

### Vergleich der Eingabeauflösungen

Neben der ursprünglichen Auflösung von $224 \times 224$ Pixeln aus CheXNet [1] wurde eine höhere Eingabeauflösung von $448 \times 448$ Pixeln untersucht. Die Originalaufnahmen des Datensatzes liegen teilweise mit einer Auflösung von bis zu $1024 \times 1024$ Pixeln vor [2].

Die Untersuchung sollte zeigen, ob kleinere Bildstrukturen bei höherer Eingabeauflösung besser erhalten bleiben und dadurch insbesondere die Erkennung von Nodule und Mass verbessert wird. Gleichzeitig erhöht sich durch die Verdopplung von Breite und Höhe der Rechen- und Speicherbedarf ungefähr um den Faktor vier.

Die Ergebnisse der beiden Auflösungen werden anhand der Macro-AUC sowie der ROC-AUC der einzelnen Pathologien verglichen:

Eingabeauflösung	Macro-AUC	Nodule	Mass
$224 \times 224$	…	…	…
$448 \times 448$	…	…	…

Der Vergleich dient als Grundlage für die Entscheidung über die im finalen Modell verwendete Eingabeauflösung.

Quellen
[1] Rajpurkar, P. et al. (2017): CheXNet: Radiologist-Level Pneumonia Detection on Chest X-Rays with Deep Learning.

[2] Wang, X. et al. (2017): ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks on Weakly-Supervised Classification and Localization of Common Thorax Diseases.

[3] Selvaraju, R. R. et al. (2017): Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization.

## Architecture Migration: From Django + Next.js to Spring Boot + Thymeleaf

This sections describes our (small) odysee until we arrived at the current application.

### Why we basically built this project twice

Something that isn't really covered in the paper but is something we still wanted to document: we didn't build the app once, we (basically) built it twice. The first version was Django (backend) + React/Next.js (frontend), the second one is Spring Boot with a server-rendered Thymeleaf frontend, which is also the final results. So the following describes a) how we got there and b) what this meant for the architecture.

### Starting point: Django + React

The original decision to go with Django was mostly practical: we already had experience with Python, and since the machine learning model was going to be in Python (PyTorch) anyways, it made sense to keep the model and the backend in the same language and ecosystem. The idea was to have patient management and the AI analysis live together in the Django backend, without putting an extra service boundary in between.

The backend was split into three Django apps (`patients`, `imaging`, `ml`), each with its own models, DRF serializers and views/viewsets. Patient data was exposed through a REST API, and the plan was to keep the UI side as simple as possible. The problem came with a requirement that wasn't thought through enough in the original concept: file uploads. For uploading X-rays (and later attachments like PDF reports) we needed a frontend that could actually handle forms, file inputs and async feedback while the AI analysis was running. Plain server-side templating in Django would've technically been possible, but we didn't think it was flexible enough for the interactivity we wanted (e.g. showing the Grad-CAM overlay live, clicking through finding cards). So Next.js got added on top as a separate frontend that consumed the Django REST API. 

### Why that turned into a problem

That combination led to a bunch of follow-up problems over the course of the project. Individually they each seemed small, but together they made the architecture way messier than originally intended:

- **Two servers instead of one.** Django/DRF on one side, Next.js on the other. Both had to be deployed (into the cloud) and configured independently and kept in sync — overhead that really shouldn't have been necessary for a prototype of this size.
- **Three different language/tech worlds at once.** Python for Django and the ML model, TypeScript/React for the frontend with Next.js by its side (another server framework than Django working differently from Django), plus CSS modules and JSX for styling. Strictly speaking, each of these worlds would've needed its own documentation, its own conventions and its own testing. This drove up both the documentation effort (even for only two people working on the project) and the ramp-up time for anyone new to the project more than it should have.
- **Confusing "magic" wiring on the Django side.** Django and DRF do a lot of stuff implicitly for you (serializer interactions, automatic routing through viewsets, signal-like mechanisms). That's productive as long as you stay exactly within the intended pattern, but it makes the code a lot harder to follow the moment you step outside of it and that kept happening constantly for us because of the combination of patient management, file handling and ML integration.
- **Validation was split across two sides.** Part of the validation logic lived server-side in the Django models/serializers, and another part was manually rebuilt client-side in the React form components. For a validation error to actually show up correctly for the user, it first had to come back from the backend as an error object over the REST interface, get parsed in the frontend, and then get matched to the right form field. That meant more code and more places for things to go wrong — and from a regulatory point of view it also just wasn't clean, since validation wasn't a single, traceable process in one place. Aditionally this also made testing more complex, since similar (almost identical) errors had to be written for frontend and backend to encure consistency (e.g. for validation).

The end result was an architecture that technically worked, but was spread across two folders, two server processes and three languages, was more complex than it needed to be for a prototype this size, and had validation logic that wasn't great going forward given later regulatory requirements (traceability, consistency — see the MDR chapter) and made testing more difficulty than it needed to be.

### The decision: Spring Boot + Thymeleaf

As a consequence, we decided to rebuild the patient management side of the app from scratch — this time as a Spring Boot monolith with Thymeleaf as a server-rendered frontend, instead of a separate Django backend with Next.js bolted on in front of it.

The reasoning comes down to four points:

1. **Less implicit magic, more traceability.** Spring Boot still takes away a lot of boilerplate, but it keeps a lot more of it explicitly visible in the code (controllers, services, repositories as clearly separated, manually wired layers instead of auto-generated viewset logic). For a project that's ultimately also going to be evaluated on traceability and documentability — which the MDR explicitly requires for software as a medical device — that mattered a lot.
2. **Validation lives in exactly one place.** With Jakarta Bean Validation the entire validation logic can be declared directly on the form objects in the backend. Since Thymeleaf renders the forms in the same process, validation errors can be shown directly on the relevant form field via `BindingResult` and `th:errors`, with no detour through a REST interface. There's no second place left where validation rules can end up duplicated or maintained independently.
3. **Frontend directly integrated into the backend.** Because Thymeleaf is part of the same Spring Boot application, there's no separate frontend deployment and no CORS setup between two servers anymore. That doesn't just cut down the number of moving parts in the system, it's also a win from a regulatory angle: there's only one component left that interacts with the user and controls rendering, validation and data access — which makes it a lot easier to scope what actually needs to be reviewed and documented.
4. **The ML component stays cleanly separated.** The one part that deliberately did *not* move into the Spring Boot monolith is the machine learning component itself. It stays a standalone Python service (FastAPI) accessed over a REST interface. That separation mattered to us because PyTorch/Grad-CAM doesn't really translate to the JVM anyway, and because it matches what we described in the concept: patient management and AI analysis stay as interchangeable, independently deployable components that only talk to each other through a defined interface — just now with only one language (Java) on the application side instead of two.

### Takeaway

The first, Django/Next.js-based version wasn't wasted effort, it was more of a necessary intermediate step to actually figure out what requirements (file uploads, validation, wiring in the AI results) the system puts on the architecture in the first place. Only with that knowledge did it become possible to design a noticeably simpler, more consistent solution on the second attempt. From the software-as-a-medical-device perspective (chapter VIII), switching wasn't just a matter of taste but a substantive decision: an architecture with fewer moving parts, centralized validation and a single component responsible for user interaction is a lot easier to document traceably, write tests for and evaluate against the MDR than two apps in different languages loosely coupled over REST.