# Documentation of developing process

This documentation describes any additional information we want to provide you (the reader) about our project. This mainly includes a description our descisions regarding the machine learning model and the development of our application.

## Machine Learning

### Machine Learning Model

The machine learning component was developed based on the architectural and modeling decisions of CheXNet by Rajpurkar et al. [1]. The goal was to detect abnormalities in chest X-rays.

A DenseNet-121 model pre-trained on ImageNet was used as the foundation and further trained on the NIH Chest X-ray Dataset. The architecture was adapted to meet the requirements of the developed prototype.

### Data Set and Data Split

The NIH Chest X-ray Dataset, comprising 112,120 X-ray images from 30,805 patients and representing 14 thoracic pathologies, served as the data set [2].

The official training and test lists from the dataset were used for the split. Additionally, a separate validation dataset was created from the training data. The split was performed at the patient level, ensuring that images from a single patient do not appear simultaneously in the training, validation, and test datasets.

To ensure this technically, three overlap checks between the training, validation, and test data were implemented and verified using assertions. This prevents data from the same patient from being accidentally used in multiple datasets.

### Model Architecture and Classification Task

DenseNet-121 was chosen as the model because this architecture is also used in CheXNet for the NIH Chest X-ray Dataset [1].

The original classification head of the pre-trained model was replaced with a custom classification head containing 14 output neurons. Each output corresponds to one of the 14 pathologies in the dataset. Since multiple pathologies can occur simultaneously, the task was implemented as multi-label classification.

The classification head also includes a dropout layer with $p=0.25$. The model initially outputs logits, which are converted into probabilities between 0 and 1 during inference using the sigmoid function.

“No Finding” was not modeled as a separate output class. This outcome is implicitly assumed when none of the 14 pathologies exceeds the respective classification threshold.

### Training Procedure

Training was carried out in two phases. First, the trainable parameters were restricted to the newly added classification head. Subsequently, the backbone was made available for fine-tuning and further trained with a lower learning rate.

BCEWithLogitsLoss was used as the loss function. This function is suitable for the multi-label classification used here and combines the sigmoid function with binary cross-entropy in a numerically stable form.

Since the pathologies occur with varying frequencies in the training dataset, class-dependent pos_weight values were used. These were derived from the class distribution of the training dataset. To limit the weighting of very rare classes, the values were additionally adjusted using square-root damping.

Model Selection and Evaluation

The Macro-AUC on the validation dataset was used to select the best model state. In this process, the ROC-AUC values for each of the 14 pathologies are averaged so that each class is given equal consideration regardless of its frequency.

The best result observed on the validation dataset was:

Validation Macro-AUC: 0.8322

Classification thresholds for the individual pathologies were then determined using the Youden index on the validation dataset. The thresholds determined were applied unchanged to the test dataset. The test data were therefore not used to optimize the thresholds.

Explainability and Integration

The probabilities calculated by the model are used in the prototype to visualize the detected pathologies. In addition, Grad-CAM is used to highlight image regions relevant to a model prediction [3].

The Grad-CAM visualization serves as supplementary information to help understand the model’s decision and does not constitute an independent medical diagnosis.

### Comparison of Input Resolutions

In addition to the original resolution of $224 \times 224$ pixels used by CheXNet [1], a higher input resolution of $448 \times 448$ pixels was investigated. Some of the original images in the NIH Chest X-ray Dataset have a resolution of up to $1024 \times 1024$ pixels [2].

The purpose of this experiment was to determine whether the higher input resolution improves the classification performance by preserving more fine-grained image information. This is particularly relevant for small or localized abnormalities, where spatial information may be lost when the original images are resized to a lower resolution. At the same time, doubling both the width and height increases the number of input pixels by a factor of four, resulting in higher computational and memory requirements.

Both model variants were trained under otherwise identical conditions. The only difference between the two experiments was the input resolution. The dataset was split on patient level into training, validation, and test sets to prevent images from the same patient from occurring in multiple splits.

For both experiments, the dataset consisted of 77,988 training images from 25,207 patients, 8,536 validation images from 2,801 patients, and 25,596 test images from 2,797 patients. The model was trained as a multi-label classifier using BCEWithLogitsLoss with class-specific weights derived from the square root of the positive-class weights to account for the strong class imbalance.

Model selection was performed based on the validation macro-AUC. The best model for the $448 \times 448$ experiment was obtained after epoch 7 with a validation macro-AUC of 0.8322. The corresponding checkpoint is stored at:

./checkpoints/448px/best_model.pt

The complete training history is stored at:

./checkpoints/448px/history.json

The results for the two input resolutions are summarized below:

Input Resolution | Validation Macro-AUC | Test Macro-AUC | Test Loss
$224 \times 224$ | 0.8228 | 0.7956 | 0.5808
$448 \times 448$ | 0.8322 | 0.8071 | 0.5511

The higher input resolution resulted in an improvement in classification performance. The validation macro-AUC increased from 0.8228 to 0.8322, corresponding to an absolute improvement of 0.0094 AUC points. On the test dataset, the macro-AUC increased from 0.7956 to 0.8071, corresponding to an absolute improvement of 0.0115 AUC points. The test loss was also lower for the $448 \times 448$ model, decreasing from 0.5808 to 0.5511.

Based on the improved validation and test performance, the $448 \times 448$ input resolution was selected for the final model. The detailed training history, including training loss, validation loss, validation macro-AUC, and learning-rate changes, is retained in the corresponding experiment history file.

References

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