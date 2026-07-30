from rest_framework import serializers
from .models import Study, XRayImage


class StudySerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = ["id", "patient", "created_at"]
        read_only_fields = ["id", "created_at"]


class XRayImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = XRayImage
        fields = ["id", "study", "image", "uploaded_at", "prediction_status"]
        read_only_fields = ["id", "uploaded_at", "prediction_status"]

