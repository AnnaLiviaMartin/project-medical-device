from django.db import models

from patients.models import Patient

# Create your models here.
class Study(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="studies")
    created_at = models.DateTimeField(auto_now_add=True)

class XRayImage(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="images")
    image = models.FileField(upload_to="xray_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Status der Inferenz
    prediction_status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("running", "Running"),
            ("done", "Done"),
            ("failed", "Failed"),
        ],
    )