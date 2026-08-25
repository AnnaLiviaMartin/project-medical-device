# Deployment auf Azure (Student-Tarif)

Diese Anleitung deployed Backend (Django + ML-Modell) und Frontend (Next.js)
als zwei separate **Azure Container Apps**. Der Consumption-Plan skaliert
bei Inaktivität auf **0 Instanzen** herunter - bei 4 Zugriffen/Tag zahlst
du damit nur fuer die paar Sekunden tatsaechlicher Rechenzeit statt fuer
einen 24/7 laufenden Server.

## 1. Lokal testen (empfohlen, bevor es nach Azure geht)

```bash
cd xxx/project-medical-device/project
.\gradlew clean build -x test
docker compose config
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000/api/...

Wenn das lokal laeuft, funktioniert es strukturell auch in Azure - Docker
ist hier die Abstraktionsebene, die "auf meinem Rechner" und "in Azure"
identisch macht.

---

## 2. Azure CLI vorbereiten

```bash
az login
az account show   # pruefen, dass die Student-Subscription aktiv ist

RESOURCE_GROUP="medic-study-rg"
LOCATION="germanywestcentral"
ACR_NAME="medicstudyacr$RANDOM"   # muss global eindeutig sein

az group create --name $RESOURCE_GROUP --location $LOCATION

windows:
$RESOURCE_GROUP = "medic-study-rg"
$LOCATION = "germanywestcentral"
$ACR_NAME = "medicstudyacr$((Get-Random))"

```

---

## 3. Container Registry anlegen und Images bauen

`az acr build` baut die Images direkt in Azure (kein lokales Docker-Setup
mit ausreichend Ressourcen noetig, funktioniert auch von einem schwaecheren
Laptop aus).

```bash
az account show
az provider register --namespace Microsoft.ContainerRegistry --wait
az provider show --namespace Microsoft.ContainerRegistry --query registrationState -o tsv

az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic

# Backend-Image bauen (Context = Projekt-Root, siehe backend/Dockerfile)
#if:
az acr build --registry $ACR_NAME --image medic-backend:latest --file backend/Dockerfile .
#alt:
docker build -t medic-backend -f backend/Dockerfile .
az acr login --name $ACR_NAME
docker tag medic-backend:latest $ACR_NAME.azurecr.io/medic-backend:latest
docker tag medic-backend:latest medicstudyacr1288038825.azurecr.io/medic-backend:latest
docker push $ACR_NAME.azurecr.io/medic-backend:latest
docker push medicstudyacr1288038825.azurecr.io/medic-backend:latest
```

Das Frontend-Image bauen wir bewusst **erst in Schritt 6**, nachdem das
Backend deployed ist - `NEXT_PUBLIC_API_URL` wird beim Build fest ins
Next.js-Bundle eingebacken und wir brauchen dafuer die endgueltige
Backend-URL.

---

## 4. Container Apps Environment + persistenten Speicher anlegen

SQLite-Datei und hochgeladene Bilder (Roentgenbilder, Grad-CAM-Overlays)
muessen einen Container-Neustart ueberleben. Dafuer mounten wir einen
Azure Files Share.

```bash
STORAGE_ACCOUNT="medicstudystorage$RANDOM"
$STORAGE_ACCOUNT="medicdata$((Get-Random))"
FILE_SHARE="medic-data"

#$STORAGE_ACCOUNT = "medicstudystorage$((Get-Random))"
#$FILE_SHARE = "medic-data"

az provider register --namespace Microsoft.Storage --wait

az storage account create --resource-group $RESOURCE_GROUP --name $STORAGE_ACCOUNT --location $LOCATION --sku Standard_LRS

STORAGE_KEY=$(az storage account keys list --resource-group $RESOURCE_GROUP --account-name $STORAGE_ACCOUNT --query "[0].value" -o tsv)
#alt:
$STORAGE_KEY = az storage account keys list `
  --resource-group $RESOURCE_GROUP `
  --account-name $STORAGE_ACCOUNT `
  --query "[0].value" `
  -o tsv

az storage share-rm create --resource-group $RESOURCE_GROUP --storage-account $STORAGE_ACCOUNT --name $FILE_SHARE --quota 5

az containerapp env create --resource-group $RESOURCE_GROUP --name medic-env --location $LOCATION

az provider register -n Microsoft.OperationalInsights --wait

az containerapp env storage set --resource-group $RESOURCE_GROUP --name medic-env --storage-name medic-data-storage --azure-file-account-name $STORAGE_ACCOUNT --azure-file-account-key $STORAGE_KEY --azure-file-share-name $FILE_SHARE --access-mode ReadWrite
```

---

## 5. Backend deployen

Wichtige Punkte bei diesem Setup:

- **`--min-replicas 0`**: skaliert bei Inaktivitaet komplett runter (spart Credits).
- **`--max-replicas 1`**: bewusst auf 1 begrenzt. SQLite vertraegt keine
  parallelen Schreibzugriffe aus mehreren Instanzen, und jede zusaetzliche
  Instanz wuerde das ML-Modell erneut in den Speicher laden.
- **CPU/Memory**: 1 vCPU / 2 GiB als Startwert - PyTorch + Modell brauchen
  spuerbar mehr RAM als eine "normale" Django-App. Bei Bedarf mit
  `az containerapp update` nachjustieren.

```bash
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
# $ACR_LOGIN_SERVER = az acr show `
  --name $ACR_NAME `
  --query loginServer `
  -o tsv

#az acr update `
  --name $ACR_NAME `
  --admin-enabled true
# Adding registry password as a secret with name "medicstudyacr1288038825azurecrio-medicstudyacr1288038825"

az containerapp create --resource-group $RESOURCE_GROUP --name medic-backend --environment medic-env --image "$ACR_LOGIN_SERVER/medic-backend:latest" --registry-server $ACR_LOGIN_SERVER --target-port 8000 --ingress external --min-replicas 0 --max-replicas 1 --cpu 1.0 --memory 2.0Gi --env-vars DJANGO_SECRET_KEY=secretref:django-secret-key DJANGO_DEBUG=False DJANGO_ALLOWED_HOSTS=placeholder DJANGO_CORS_ALLOWED_ORIGINS=placeholder DJANGO_DB_PATH=/data/db.sqlite3 DJANGO_MEDIA_ROOT=/data/media --secrets django-secret-key="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')"

# Persistenten Storage einhaengen (aktuell nur per update-Befehl moeglich)
az containerapp update `
  --resource-group $RESOURCE_GROUP `
  --name medic-backend `
  --yaml .\backend-volume.yaml
```

Backend-URL ermitteln (wird gleich fuer CORS und das Frontend-Build gebraucht):

```bash
BACKEND_URL=$(az containerapp show --resource-group $RESOURCE_GROUP --name medic-backend --query properties.configuration.ingress.fqdn -o tsv)

echo "https://$BACKEND_URL"
# https://medic-backend.calmhill-fe300a55.germanywestcentral.azurecontainerapps.io
```

`DJANGO_ALLOWED_HOSTS` jetzt mit der echten URL setzen:

```bash
az containerapp update --resource-group $RESOURCE_GROUP --name medic-backend --set-env-vars DJANGO_ALLOWED_HOSTS="$BACKEND_URL"
```

---

## 6. Frontend bauen und deployen

> **Hinweis zu INTERNAL_API_URL:** Lokal (docker-compose) ist die Trennung
> von `NEXT_PUBLIC_API_URL` (Browser) und `INTERNAL_API_URL` (serverseitige
> Next.js-Calls im Docker-Netzwerk) noetig, weil der Next.js-Server sonst
> "localhost" mit sich selbst statt mit dem Backend-Container verwechselt.
> In Azure ist das **optional**: Backend und Frontend erreichen sich hier
> beide ueber die oeffentliche HTTPS-URL des Backends, `ALLOWED_HOSTS`
> steht dafuer bereits richtig. `INTERNAL_API_URL` kann daher weggelassen
> werden (Fallback auf `NEXT_PUBLIC_API_URL`) - oder zur Optimierung auf
> dieselbe URL gesetzt werden, das aendert nichts am Verhalten.

Jetzt, wo `$BACKEND_URL` feststeht, das Frontend-Image damit bauen:

```bash
#if
az acr build --registry $ACR_NAME --image medic-frontend:latest --file frontend/Dockerfile --build-arg NEXT_PUBLIC_API_URL="https://$BACKEND_URL" frontend
#alt
docker build `
  -t medic-frontend:latest `
  -f frontend/Dockerfile `
  --build-arg NEXT_PUBLIC_API_URL="https://$BACKEND_URL" `
  frontend
docker tag medic-frontend:latest medicstudyacr1288038825.azurecr.io/medic-frontend:latest
docker push medicstudyacr1288038825.azurecr.io/medic-frontend:latest

az containerapp create --resource-group $RESOURCE_GROUP --name medic-frontend --environment medic-env --image "$ACR_LOGIN_SERVER/medic-frontend:latest" --registry-server $ACR_LOGIN_SERVER --target-port 3000 --ingress external --min-replicas 0 --max-replicas 1 --cpu 0.5 --memory 1.0Gi

FRONTEND_URL=$(az containerapp show --resource-group $RESOURCE_GROUP --name medic-frontend --query properties.configuration.ingress.fqdn -o tsv)

echo "https://$FRONTEND_URL"
#https://medic-frontend.calmhill-fe300a55.germanywestcentral.azurecontainerapps.io
```

---

## 7. CORS final verdrahten

Jetzt, wo beide URLs feststehen, dem Backend die echte Frontend-URL fuer
CORS (und optional CSRF fuer `/admin/`) mitgeben:

```bash
az containerapp update --resource-group $RESOURCE_GROUP --name medic-backend --set-env-vars DJANGO_CORS_ALLOWED_ORIGINS="https://$FRONTEND_URL" DJANGO_CSRF_TRUSTED_ORIGINS="https://$BACKEND_URL"
```

Die App ist jetzt unter `https://$FRONTEND_URL` erreichbar.

---

## Kurz-Checkliste bei Aenderungen am Code

```bash
# Backend-Aenderung:
az acr build --registry $ACR_NAME --image medic-backend:latest --file backend/Dockerfile .
az containerapp update --resource-group $RESOURCE_GROUP --name medic-backend \
  --image "$ACR_LOGIN_SERVER/medic-backend:latest"

# Frontend-Aenderung:
az acr build --registry $ACR_NAME --image medic-frontend:latest --file frontend/Dockerfile \
  --build-arg NEXT_PUBLIC_API_URL="https://$BACKEND_URL" frontend
az containerapp update --resource-group $RESOURCE_GROUP --name medic-frontend \
  --image "$ACR_LOGIN_SERVER/medic-frontend:latest"
```

---

## Abschalten

```bash
az group delete --name medic-study-rg --yes
```