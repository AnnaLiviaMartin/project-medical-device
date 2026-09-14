# Deployment auf Azure (Student-Tarif)

Diese Anleitung deployed **zwei Azure Container Apps**, genauso wie wir es gemacht haben:

- **`medic-backend`**: Spring-Boot-App (Java 21), rendert die komplette Oberfläche selbst über Thymeleaf. Da Thymeleaf serverseitig rendert, spricht der Browser ausschließlich mit `medic-backend`, nicht direkt mit dem ML-Service.
- **`medic-ml-service`**: FastAPI + PyTorch/DenseNet-Modell. Wird ausschließlich vom Spring-Backend serverseitig aufgerufen (`RestMlAnalysisService`) - braucht daher nur **internen** Zugriff innerhalb der Container Apps Environment, keine öffentliche URL.

Der Consumption-Plan skaliert bei Inaktivität auf **0 Instanzen** herunter - bei seltenen Zugriffen zahlst du damit nur für die paar Sekunden tatsächlicher Rechenzeit statt für einen 24/7 laufenden Server. Der erste Request nach einer Ruhephase braucht dafür ein paar Sekunden länger (Cold Start).

## 1. Lokal dockern

```bash
cd projekt
./gradlew clean build
docker compose up --build
```

- App (inkl. UI): http://localhost:8080
- H2-Konsole: http://localhost:8080/h2-console
- ML-Service (intern, nur zum Debuggen direkt ansprechbar): http://localhost:8000/health

Wichtig: Der Gradle-Build (`./gradlew clean build`) muss **vor** dem Docker-Build laufen, weil das root-`Dockerfile` das fertige JAR aus `build/libs/*.jar` kopiert.

---

## 2. Azure CLI vorbereiten

```bash
az login --use-device-code
az account show   # pruefen, dass die Student-Subscription aktiv ist

RESOURCE_GROUP="medic-study-samd"
LOCATION="germanywestcentral"
ACR_NAME="medicstudyacr$RANDOM"

az group create --name $RESOURCE_GROUP --location $LOCATION
```

---

## 3. Container Registry anlegen und Images bauen

Zuerst muss der Provider registriert werden:

```bash
az provider register --namespace Microsoft.ContainerRegistry --wait
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic
```

Dann das lokale Docker laufen lassen und dieses anschließen pushen:

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

## 4. Container Apps Environment + persistenten Speicher anlegen

Die H2-Datenbankdatei und hochgeladene Bilder müssen einen Container-Neustart überleben. Dafür mounten wir einen Azure Files Share **nur ins Backend** - der ML-Service ist zustandslos.

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

## 5. ML-Service deployen (zuerst, weil intern - Backend braucht dessen URL)

Wichtige Punkte:

- **`--ingress internal`**: keine öffentliche URL, nur innerhalb der Container Apps Environment erreichbar - der Browser soll diesen Service nie direkt ansprechen können.
- **`--min-replicas 0` / `--max-replicas 1`**: spart Credits bei Inaktivität; 1 Replica reicht, das Modell muss nicht mehrfach im Speicher gehalten werden.

```bash
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
$ACR_LOGIN_SERVER = az acr show --name $ACR_NAME --query loginServer -o tsv
```

Dann sich mit dem Account Username und Passwort holen:

```bash
az acr update --name $ACR_NAME --admin-enabled true
$ACR_USERNAME = az acr credential show --name $ACR_NAME --query username -o tsv
$ACR_PASSWORD = az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv
```

Und dann die Container-App erstellen:

```bash
az containerapp create  --resource-group $RESOURCE_GROUP  --name medic-ml-service  --environment medic-env --image "$ACR_LOGIN_SERVER/medic-ml-service:latest" --registry-server $ACR_LOGIN_SERVER --target-port 8000 --ingress internal --min-replicas 0 --max-replicas 1 --cpu 1.5 --memory 3.0Gi --env-vars ML_MODEL_PATH=/app/machine_learning/checkpoints/best_model.pt ML_THRESHOLD=0.7
```

Interne URL ermitteln (wird für `ML_SERVICE_URL` im Backend benötigt):

```bash
ML_SERVICE_URL=$(az containerapp show --resource-group $RESOURCE_GROUP --name medic-ml-service --query properties.configuration.ingress.fqdn -o tsv)
$ML_SERVICE_URL=$(az containerapp show --resource-group $RESOURCE_GROUP --name medic-ml-service --query properties.configuration.ingress.fqdn -o tsv)

echo "https://$ML_SERVICE_URL"
# https://medic-ml-service.internal.wittyglacier-cf4c034a.germanywestcentral.azurecontainerapps.io
```

---

## 6. Backend deployen

Wichtige Punkte:

- **`--min-replicas 0`**: skaliert bei Inaktivität komplett runter.
- **`--max-replicas 1`**: bewusst auf 1 begrenzt - H2 (Datei-DB) verträgt keine parallelen Schreibzugriffe aus mehreren Instanzen.
- **`ML_ANALYSIS_PROVIDER=rest`**: schaltet von der eingebauten `simulated`- Analyse (Default, keine externe Abhängigkeit) auf den echten Aufruf des
  ML-Service um.
- Storage wird erst per `az containerapp update --yaml` eingehängt (aktuell bei `containerapp create` mit Volume-Mounts über die CLI nicht direkt möglich).

```bash
az containerapp create  --resource-group $RESOURCE_GROUP  --name medic-backend --environment medic-env  --image "$ACR_LOGIN_SERVER/medic-backend:latest"  --registry-server $ACR_LOGIN_SERVER --target-port 8080  --ingress external  --min-replicas 0 --max-replicas 1 --cpu 1.0  --memory 2.0Gi  --env-vars SPRING_DATASOURCE_URL=jdbc:h2:file:/data/h2/database UPLOAD_DIR=/data/uploads ATTACHMENT_SUBDIR=attachments XRAY_SUBDIR=xray_images GRADCAM_SUBDIR=gradcam ML_ANALYSIS_PROVIDER=rest ML_SERVICE_URL="https://$ML_SERVICE_URL" ML_SERVICE_TIMEOUT_SECONDS=60
```

Persistenten Storage muss noch eingehängt werden. Dafür eine `backend-volume.yaml` erstellen:

```bash
az containerapp update  --resource-group $RESOURCE_GROUP  --name medic-backend  --yaml backend-volume.yaml
```

Backend-URL ermitteln:

```bash
BACKEND_URL=$(az containerapp show --resource-group $RESOURCE_GROUP --name medic-backend --query properties.configuration.ingress.fqdn -o tsv)
$BACKEND_URL=$(az containerapp show --resource-group $RESOURCE_GROUP --name medic-backend --query properties.configuration.ingress.fqdn -o tsv)

echo "https://$BACKEND_URL"
# https://medic-backend.wittyglacier-cf4c034a.germanywestcentral.azurecontainerapps.io
```

Die App ist jetzt unter `https://$BACKEND_URL/patients` erreichbar.

---

## Checkliste bei Änderungen am Code

Für das Neubauen von Frontend und Backend: siehe [Schritt 3](#3-container-registry-anlegen-und-images-bauen) für die Anleitung über Docker und push

```bash
# Backend-Änderung:
./gradlew clean build
docker build -t medic-backend:v2 -f Dockerfile .
az acr login --name $ACR_NAME
docker tag medic-backend:v2 $ACR_LOGIN_SERVER/medic-backend:v2
az containerapp update --resource-group $RESOURCE_GROUP --name medic-backend --image "$ACR_LOGIN_SERVER/medic-backend:v2"

# ML-Service-Änderung:
docker build -t medic-ml-service:v2 -f ml-service/Dockerfile ml-service
docker tag medic-ml-service:v2 $ACR_LOGIN_SERVER/medic-ml-service:v2
docker push $ACR_LOGIN_SERVER/medic-ml-service:v2
az containerapp update --resource-group $RESOURCE_GROUP --name medic-ml-service  --image "$ACR_LOGIN_SERVER/medic-ml-service:v2"
```

## Abschalten

```bash
az group delete --name medic-study-rg --yes
```
