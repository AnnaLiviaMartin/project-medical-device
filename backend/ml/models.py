from django.db import models

from imaging.models import XRayImage

# Create your models here.
class Prediction(models.Model):
    xray_image = models.OneToOneField(XRayImage, on_delete=models.CASCADE, related_name="prediction")
    label = models.CharField(max_length=100)
    confidence = models.FloatField()
    raw_result = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)