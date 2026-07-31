from django.db import models
from patients.models import Patient


class Study(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="studies")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Study {self.pk} - {self.patient}"


class XRayImage(models.Model):
    class PredictionStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        DONE = "done", "Done"
        FAILED = "failed", "Failed"

    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="xray_images")
    image = models.ImageField(upload_to="xray_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    prediction_status = models.CharField(
        max_length=20, choices=PredictionStatus.choices, default=PredictionStatus.PENDING
    )

    def __str__(self):
        return f"XRay {self.pk} for Study {self.study_id}"