from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Study, XRayImage
from .serializers import StudySerializer, XRayImageSerializer
from ml.models import Prediction
from ml.services import run_model_on_image
from patients.models import HistoryEntry


class StudyViewSet(ModelViewSet):
    serializer_class = StudySerializer

    def get_queryset(self):
        queryset = Study.objects.all().order_by("id")
        patient_id = self.request.query_params.get("patient")
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset


class XRayImageViewSet(ModelViewSet):
    queryset = XRayImage.objects.all().order_by("id")
    serializer_class = XRayImageSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image = None
        try:
            with transaction.atomic():
                image = serializer.save(prediction_status="running")
                result = run_model_on_image(image.image.path)

                Prediction.objects.update_or_create(
                    xray_image=image,
                    defaults={
                        "label": result["label"],
                        "confidence": result["confidence"],
                        "raw_result": result,
                    },
                )
                image.prediction_status = "done"
                image.save(update_fields=["prediction_status"])

        except Exception as exc:
            if image is not None:
                image.prediction_status = "failed"
                image.save(update_fields=["prediction_status"])

            return Response(
                {"detail": f"Inferenz fehlgeschlagen: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        output_serializer = self.get_serializer(image)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class HistoryScanUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, patient_id, entry_id):
        entry = get_object_or_404(
            HistoryEntry, pk=entry_id, patient_id=patient_id
        )

        file = request.data.get("file")
        if not file:
            return Response(
                {"detail": "Keine Datei übermittelt."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if entry.study_id is None:
            study = Study.objects.create(patient_id=patient_id)
            entry.study = study
            entry.save(update_fields=["study"])
        else:
            study = entry.study

        image = None
        try:
            with transaction.atomic():
                image = XRayImage.objects.create(
                    study=study, image=file, prediction_status="running"
                )
                result = run_model_on_image(image.image.path)

                Prediction.objects.update_or_create(
                    xray_image=image,
                    defaults={
                        "label": result["label"],
                        "confidence": result["confidence"],
                        "raw_result": result,
                    },
                )
                image.prediction_status = "done"
                image.save(update_fields=["prediction_status"])

        except Exception as exc:
            if image is not None:
                image.prediction_status = "failed"
                image.save(update_fields=["prediction_status"])

            return Response(
                {"detail": f"Inferenz fehlgeschlagen: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = XRayImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)