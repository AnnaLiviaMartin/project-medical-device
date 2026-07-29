from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Patient
from .serializers import PatientSerializer

# Create your views here -> Controller.
class PatientViewSet(ModelViewSet):
    queryset = Patient.objects.all().order_by("id")
    serializer_class = PatientSerializer