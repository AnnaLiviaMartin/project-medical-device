from django.db import models

# Create your models here -> database entities.

class Sex(models.TextChoices):
      FEMALE = "female", "Female"
      MALE = "male", "Male"
      OTHER = "other", "Other"

class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(
        max_length=10,
        choices=Sex.choices,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.last_name}, {self.first_name}"