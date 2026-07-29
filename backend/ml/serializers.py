from rest_framework import serializers
from .models import Prediction

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ["id", "xray_image", "label", "confidence", "raw_result", "created_at"]
        read_only_fields = fields
