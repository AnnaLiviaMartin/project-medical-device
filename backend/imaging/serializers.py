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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # DRF's ImageField gibt bei vorhandenem "request" im Context
        # standardmaessig eine absolute URL zurueck (host-abhaengig - siehe
        # Kommentar in patients/serializers.py). Hier stattdessen immer die
        # relative URL erzwingen; das Frontend haengt die fuer den Browser
        # richtige Basis-URL selbst an.
        if instance.image:
            data["image"] = instance.image.url
        return data

