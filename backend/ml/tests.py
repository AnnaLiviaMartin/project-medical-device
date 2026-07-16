from django.test import TestCase
from patients.models import Patient
from imaging.models import Study

class PredictionModelTest(TestCase):
    def test_prediction_creation(self):
        patient = Patient.objects.create(
            first_name="Fiona",
            last_name="Model",
            sex="female",
        )
        study = Study.objects.create(patient=patient)