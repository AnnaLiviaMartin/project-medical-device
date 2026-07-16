from rest_framework import serializers
from .models import Study

class StudySerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = ["id", "patient", "created_at", "xray_file"]
        read_only_fields = ["id", "created_at"]
