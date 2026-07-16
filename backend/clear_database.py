from imaging.models import Study
from patients.models import Patient

Study.objects.all().delete()
Patient.objects.all().delete()
