# From Model to Prototype: A User-Centred Workflow for Cloud-Based AI-Assisted Chest X-Ray Analysis

This is the repository to the paper: "From Model to Prototype: A User-Centred Workflow for Cloud-Based AI-Assisted Chest X-Ray Analysis" by Anna-Livia Martin and David Rossel

The documentation including more information about the process of developting the prototype can be found at the [Doku](./DOCU.md).

The URL to Azure is: https://medic-backend.wittyglacier-cf4c034a.germanywestcentral.azurecontainerapps.io

## Repository structure

- `machine_learning/` — PyTorch-based training, data loading, evaluation, and visualisation scripts for the NIH Chest X-ray dataset.
- `notes_and_diagrams/` — Notes, diagrams, and other material used during the development of the project and preparation of the paper.
- `paper/` — The paper associated with this project in PDF format.
- `project/` — Source code of the web-based application. The application consists of a Spring Boot backend and a FastAPI-based machine-learning service. See the README files within the directory for instructions on how to run the application locally.
- `screen_recording/` — Screen recording demonstrating the use of the web application.
- `user_study_think-aloud/` — Materials and results from the think-aloud study, including interview questions and participant results. The study material is in German.
- `user_study_ueq/` — Results of the User Experience Questionnaire (UEQ).
- `DEPLOYMENT.md` — Documentation of the deployment process and configuration of the application.
- `DOCU.md` — Documentation  including more information about the development process.
- `README.md` — What you are currently reading.

## Machine learning

The machine-learning modell is developed through several files:

- `machine_learning/nih_dataloader.py` — NIH dataset loader, label encoding, and patient-level split
- `machine_learning/nih_train.py` — DenseNet-121 training loop, validation, checkpointing, and test evaluation
- `machine_learning/x-ray-analysis.py` — evaluation entrypoint for the trained model
- `machine_learning/nih-visualize.py` — visualization of the model results
- `machine_learning/constants.py` — list of constants used for the ml model
- `machine_learning/analyse.py` — analyse probability for one image (without fastapi server)

### How to run

Install the required Python packages for training and evaluation.

```bash
cd machine_learning
python -m venv .venv
.\.venv\Scripts\activate
```

Train or evaluate the model with the available scripts:

```bash
python x-ray-analysis.py
```

## AI Usage

Information on AI usage for the paper can be found in the paper.

1. Machine learning
AI was used extensively as a supporting tool during the development of the machine learning model. In the initial development phase in particular, AI was utilised to provide an initial guide for the structure of the pipeline and possible approaches. This included, amongst other things, loading and preparing the data, loading or integrating the model, as well as training and validation. To assess and validate the proposed approaches, examples and implementations from public Git repositories were also consulted and compared with one another. On this basis, an approach suitable for the project was selected and subsequently replicated and adapted in-house.

AI was also used during the model tuning process to suggest possible adjustments to hyperparameters, input resolutions and other training configurations. These suggestions were used as a basis for designing and prioritising experiments. The resulting configurations were subsequently tested and evaluated independently using the defined validation metrics. AI was therefore used to support the exploration of possible configurations, but the final selection of the model and its parameters was based on the experimental results.

AI was also used to assist with the implementation and formulation of the code when creating the visualisations.

The AI-generated suggestions were not adopted without scrutiny, but were checked for their functionality, plausibility and suitability for the specific model.

2. Web Application
The second prototype (using Spring and FastAPI) was initially generated using Claude, based on the existing Django app. This primarily involved simpler components (e.g. entities, services, controllers, HTML pages), which simply had to be ‘adopted’ by Django and did not require any changes to the logic. Logic was then built upon this generated code. Test cases were designed with the aid of AI (ChatGPT) to achieve the highest possible coverage.

3. Literature
During the literature review, ChatGPT was used for initial orientation and to select the first potentially relevant papers. The actual analysis – reading and evaluating the papers, as well as drawing conclusions regarding their content – was carried out without the support of AI.