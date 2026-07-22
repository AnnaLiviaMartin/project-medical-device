from django.db import models

# Create your models here -> database entities.

class Sex(models.TextChoices):
    FEMALE = "female", "Female"
    MALE = "male", "Male"
    DIVERSE = "diverse", "Diverse"


class PatientStatus(models.TextChoices):
    INPATIENT = "Inpatient"
    OUTPATIENT = "Outpatient"


class Patient(models.Model):
    # Basic info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(
        max_length=10,
        choices=Sex.choices,
        blank=True,
    )

    diagnosis = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=12,
        choices=PatientStatus.choices,
        default=PatientStatus.OUTPATIENT,
    )
    last_visit = models.DateField(null=True, blank=True)
    next_appointment = models.DateField(null=True, blank=True)
    doctor = models.CharField(max_length=150, blank=True)
    ward = models.CharField(max_length=150, blank=True)

    # Address
    address_street = models.CharField(max_length=255, blank=True)
    address_zip = models.CharField(max_length=20, blank=True)
    address_city = models.CharField(max_length=150, blank=True)

    # Emergency contact
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_relation = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=50, blank=True)

    # Insurance
    insurance_provider = models.CharField(max_length=150, blank=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True)

    # Vitals (latest snapshot)
    vitals_blood_pressure = models.CharField(max_length=30, blank=True)
    vitals_heart_rate = models.CharField(max_length=30, blank=True)
    vitals_oxygen_saturation = models.CharField(max_length=30, blank=True)
    vitals_temperature = models.CharField(max_length=30, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.last_name}, {self.first_name}"

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        from datetime import date
        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )


class Allergy(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="allergies"
    )
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Medication(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="medications"
    )
    name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=100, blank=True)
    schedule = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} ({self.dosage})"