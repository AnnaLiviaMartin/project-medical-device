from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Study
from .serializers import StudySerializer

# Create your views here.

class XRayImageViewSet(ModelViewSet):
    queryset = Study.objects.all().order_by("id")
    serializer_class = StudySerializer
    parser_classes = [MultiPartParser, FormParser]
