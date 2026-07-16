from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "id",
            "patient_id",
            "first_name",
            "last_name",
            "date_of_birth",
            "sex",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
