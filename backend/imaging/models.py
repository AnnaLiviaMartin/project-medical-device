from django.db import models

from patients.models import Patient

# Create your models here.
class Study(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="studies")
    created_at = models.DateTimeField(auto_now_add=True)
    xray_file = models.FileField(upload_to="studies/", null=True, blank=True)