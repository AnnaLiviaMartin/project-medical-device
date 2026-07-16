from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .services import run_model_on_image

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from imaging.models import XRayImage
from .serializers import PredictionSerializer

class PredictionByImageView(APIView):
    def get(self, request, image_id):
        try:
            image = XRayImage.objects.get(id=image_id)
        except XRayImage.DoesNotExist:
            return Response({"detail": "Bild nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

        if not hasattr(image, "prediction"):
            return Response({"detail": "Kein Ergebnis vorhanden."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PredictionSerializer(image.prediction_status)
        return Response(serializer.data)

