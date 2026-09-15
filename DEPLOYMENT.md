# Deployment to Azure (Student plan)

This guide deploys **two Azure Container Apps**, exactly as we did:

- **`medic-backend`**: Spring Boot app (Java 21), which renders the entire user interface itself using Thymeleaf. As Thymeleaf renders on the server-side, the browser communicates exclusively with `medic-backend`, not directly with the ML service.
- **`medic-ml-service`**: FastAPI + PyTorch/DenseNet model. Is called exclusively by the Spring backend on the server-side (`RestMlAnalysisService`) – therefore requires only **internal** access within the Container Apps environment, no public URL.

The consumption plan scales down to **0 instances** during periods of inactivity – so, with infrequent access, you only pay for the few seconds of actual computing time rather than for a server running 24/7. The first request after a period of inactivity will therefore take a few seconds longer (cold start).

## 1. Docker locally

```bash
cd projekt
./gradlew clean build
docker compose up --build
```

- App (including UI): http://localhost:8080
- H2 console: http://localhost:8080/h2-console
- ML service (internal, accessible directly for debugging purposes only): http://localhost:8000/health

Important: The Gradle build (`./gradlew clean build`) must run **before** the Docker build, because the root `Dockerfile` copies the finished JAR from `build/libs/*.jar`.

---

## 2. Preparing the Azure CLI

```bash
az login --use-device-code
az account show    # check that the student subscription is active

RESOURCE_GROUP="medic-study-samd"
LOCATION="germanywestcentral"
ACR_NAME="medicstudyacr$RANDOM"

az group create --name $RESOURCE_GROUP --location $LOCATION
```

---

## 3. Creating a container registry and building images

First, the provider must be registered:

```bash
az provider register --namespace Microsoft.ContainerRegistry --wait
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic
```

Then run Docker locally and push this to GitHub:

```bash
docker build -t medic-backend -f Dockerfile .
docker build -t medic-ml-service -f ml-service/Dockerfile ml-service

az acr login --name $ACR_NAME

docker tag medic-backend:latest $ACR_NAME.azurecr.io/medic-backend:latest
docker tag medic-ml-service:latest $ACR_NAME.azurecr.io/medic-ml-service:latest
docker push $ACR_NAME.azurecr.io/medic-backend:latest
docker push $ACR_NAME.azurecr.io/medic-ml-service:latest
```

---

## 4. Setting up the container apps environment and persistent storage

The H2 database file and uploaded images must survive a container restart. To achieve this, we mount an Azure Files share **only in the backend** – the ML service is stateless.

```bash
STORAGE_ACCOUNT="medicdata$RANDOM"
FILE_SHARE="medic-data"

az provider register --namespace Microsoft.Storage --wait
az provider register --namespace Microsoft.OperationalInsights --wait

az storage account create --resource-group $RESOURCE_GROUP --name $STORAGE_ACCOUNT --location $LOCATION --sku Standard_LRS

STORAGE_KEY=$(az storage account keys list --resource-group $RESOURCE_GROUP --account-name $STORAGE_ACCOUNT --query "[0].value" -o tsv)

az storage share-rm create --resource-group $RESOURCE_GROUP --storage-account $STORAGE_ACCOUNT --name $FILE_SHARE --quota 5
az containerapp env create --resource-group $RESOURCE_GROUP --name medic-env --location $LOCATION
az containerapp env storage set --resource-group $RESOURCE_GROUP --name medic-env --storage-name medic-data-storage --azure-file-account-name $STORAGE_ACCOUNT --azure-file-account-key $STORAGE_KEY --azure-file-share-name $FILE_SHARE --access-mode ReadWrite
```

---

## 5. Deploy the ML service (first, as it’s internal – the backend needs its URL)

Key points:

- **`--ingress internal`**: no public URL; accessible only within the Container Apps environment – the browser should never be able to access this service directly.
- **`--min-replicas 0` / `--max-replicas 1`**: saves credits during periods of inactivity; 1 replica is sufficient – the model does not need to be kept in memory multiple times.

```bash
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
$ACR_LOGIN_SERVER = az acr show --name $ACR_NAME --query loginServer -o tsv
```

Then get your account username and password:

```bash
az acr update --name $ACR_NAME --admin-enabled true
$ACR_USERNAME = az acr credential show --name $ACR_NAME --query username -o tsv
$ACR_PASSWORD = az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv
```

And then create the container app:

```bash
az containerapp create  --resource-group $RESOURCE_GROUP  --name medic-ml-service  --environment medic-env --image "$ACR_LOGIN_SERVER/medic-ml-service:latest" --registry-server $ACR_LOGIN_SERVER --target-port 8000 --ingress internal --min-replicas 0 --max-replicas 1 --cpu 1.5 --memory 3.0Gi --env-vars ML_MODEL_PATH=/app/machine_learning/checkpoints/best_model.pt ML_THRESHOLD=0.7
```

Determine the internal URL (required for `ML_SERVICE_URL` in the backend):

```bash
ML_SERVICE_URL=$(az containerapp show --resource-group $RESOURCE_GROUP --name medic-ml-service --query properties.configuration.ingress.fqdn -o tsv)
$ML_SERVICE_URL=$(az containerapp show --resource-group $RESOURCE_GROUP --name medic-ml-service --query properties.configuration.ingress.fqdn -o tsv)

echo "https://$ML_SERVICE_URL"
# https://medic-ml-service.internal.wittyglacier-cf4c034a.germanywestcentral.azurecontainerapps.io
```

---

## 6. Backend deployen

Key points:

- **`--min-replicas 0`**: scales down completely during periods of inactivity.
- **`--max-replicas 1`**: deliberately limited to 1 – H2 (file-based database) cannot handle concurrent write operations from multiple instances.
- **`ML_ANALYSIS_PROVIDER=rest`**: switches from the built-in `simulated` analysis (default, no external dependency) to the actual call to the
  ML service.
- Storage is only mounted via `az containerapp update --yaml` (currently not directly possible with `containerapp create` using volume mounts via the CLI).

```bash
az containerapp create  --resource-group $RESOURCE_GROUP  --name medic-backend --environment medic-env  --image "$ACR_LOGIN_SERVER/medic-backend:latest"  --registry-server $ACR_LOGIN_SERVER --target-port 8080  --ingress external  --min-replicas 0 --max-replicas 1 --cpu 1.0  --memory 2.0Gi  --env-vars SPRING_DATASOURCE_URL=jdbc:h2:file:/data/h2/database UPLOAD_DIR=/data/uploads ATTACHMENT_SUBDIR=attachments XRAY_SUBDIR=xray_images GRADCAM_SUBDIR=gradcam ML_ANALYSIS_PROVIDER=rest ML_SERVICE_URL="https://$ML_SERVICE_URL" ML_SERVICE_TIMEOUT_SECONDS=60
```

Persistent storage still needs to be mounted. To do this, create a `backend-volume.yaml` file:

```bash
az containerapp update  --resource-group $RESOURCE_GROUP  --name medic-backend  --yaml backend-volume.yaml
```

Determine backend URL:

```bash
BACKEND_URL=$(az containerapp show --resource-group $RESOURCE_GROUP --name medic-backend --query properties.configuration.ingress.fqdn -o tsv)
$BACKEND_URL=$(az containerapp show --resource-group $RESOURCE_GROUP --name medic-backend --query properties.configuration.ingress.fqdn -o tsv)

echo "https://$BACKEND_URL"
# https://medic-backend.wittyglacier-cf4c034a.germanywestcentral.azurecontainerapps.io
```

The app is now available at `https://$BACKEND_URL/patients`.

---

## Checkliste bei Änderungen am Code

To rebuild the front-end and back-end: see [Step 3](#3-creating-a-container-registry-and-building-images) for instructions on using Docker and pushing images

```bash
# Backend-changes:
./gradlew clean build
docker build -t medic-backend:v2 -f Dockerfile .
az acr login --name $ACR_NAME
docker tag medic-backend:v2 $ACR_LOGIN_SERVER/medic-backend:v2
az containerapp update --resource-group $RESOURCE_GROUP --name medic-backend --image "$ACR_LOGIN_SERVER/medic-backend:v2"

# ML-Service-changes:
docker build -t medic-ml-service:v2 -f ml-service/Dockerfile ml-service
docker tag medic-ml-service:v2 $ACR_LOGIN_SERVER/medic-ml-service:v2
docker push $ACR_LOGIN_SERVER/medic-ml-service:v2
az containerapp update --resource-group $RESOURCE_GROUP --name medic-ml-service  --image "$ACR_LOGIN_SERVER/medic-ml-service:v2"

# Update backend when having updated ml-service
az containerapp update --resource-group $RESOURCE_GROUP --name medic-backend --set-env-vars "ML_ANALYSIS_PROVIDER=rest" "ML_SERVICE_URL=https://$ML_SERVICE_URL" "ML_SERVICE_TIMEOUT_SECONDS=60"
# az containerapp revision list --resource-group $RESOURCE_GROUP --name medic-backend -o table
```

## Switch off

```bash
az group delete --name medic-study-rg --yes
```
