from django.db import models


class Patient(models.Model):
    class Sex(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        DIVERSE = "diverse", "Diverse"

    class Status(models.TextChoices):
        OUTPATIENT = "Outpatient", "Outpatient"
        INPATIENT = "Inpatient", "Inpatient"

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=10, choices=Sex.choices)
    diagnosis = models.CharField(max_length=255)
    doctor = models.CharField(max_length=150)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OUTPATIENT, blank=True)
    last_visit = models.DateField(null=True, blank=True)
    next_appointment = models.DateField(null=True, blank=True)
    ward = models.CharField(max_length=150, blank=True, default="")

    address_street = models.CharField(max_length=255, blank=True, default="")
    address_zip = models.CharField(max_length=20, blank=True, default="")
    address_city = models.CharField(max_length=150, blank=True, default="")

    emergency_contact_name = models.CharField(max_length=150, blank=True, default="")
    emergency_contact_relation = models.CharField(max_length=100, blank=True, default="")
    emergency_contact_phone = models.CharField(max_length=50, blank=True, default="")

    insurance_provider = models.CharField(max_length=150, blank=True, default="")
    insurance_policy_number = models.CharField(max_length=100, blank=True, default="")

    vitals_blood_pressure = models.CharField(max_length=50, blank=True, default="")
    vitals_heart_rate = models.CharField(max_length=50, blank=True, default="")
    vitals_oxygen_saturation = models.CharField(max_length=50, blank=True, default="")
    vitals_temperature = models.CharField(max_length=50, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Allergy(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="allergies")
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Medication(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medications")
    name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=50)
    schedule = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.dosage})"


class HistoryEntry(models.Model):
    class Category(models.TextChoices):
        VISIT = "Visit", "Visit"
        PROCEDURE = "Procedure", "Procedure"
        FINDING = "Finding", "Finding"
        MEDICATION = "Medication", "Medication"
        FOLLOW_UP = "Follow-up", "Follow-up"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="history_entries")
    study = models.ForeignKey(
        "imaging.Study",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="history_entries",
    )
    date = models.DateField()
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField(blank=True)
    doctor = models.CharField(max_length=150, blank=True)
    department = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.title} ({self.date})"


class Attachment(models.Model):
    history_entry = models.ForeignKey(
        HistoryEntry, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(upload_to="attachments/")
    original_filename = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_filename or self.file.name

    def save(self, *args, **kwargs):
        if not self.original_filename and self.file:
            self.original_filename = self.file.name
        super().save(*args, **kwargs)