from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Patient, HistoryEntry, Attachment
from .serializers import (
    PatientListSerializer,
    PatientDetailSerializer,
    PatientCreateSerializer,
    HistoryEntrySerializer,
    AttachmentSerializer,
)


class PatientViewSet(ModelViewSet):
    queryset = Patient.objects.all().order_by("id").prefetch_related(
        "allergies", "medications"
    )

    def get_serializer_class(self):
        if self.action == "list":
            return PatientListSerializer
        if self.action in ("create", "update", "partial_update"):
            return PatientCreateSerializer
        return PatientDetailSerializer


class HistoryEntryViewSet(ModelViewSet):
    serializer_class = HistoryEntrySerializer

    def get_queryset(self):
        queryset = HistoryEntry.objects.all().order_by("-date")
        patient_id = self.request.query_params.get("patient")
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset


class AttachmentViewSet(ModelViewSet):
    serializer_class = AttachmentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = Attachment.objects.all().order_by("-uploaded_at")
        entry_id = self.kwargs.get("entry_id")
        if entry_id:
            queryset = queryset.filter(history_entry_id=entry_id)
        return queryset

    def perform_create(self, serializer):
        entry_id = self.kwargs.get("entry_id")
        serializer.save(history_entry_id=entry_id)