from django.test import TestCase
from rest_framework.test import APITestCase
from .models import Patient

class PatientModelTest(TestCase):
    def test_patient_creation(self):
        patient = Patient.objects.create(
            first_name="Anna",
            last_name="Muster",
            sex="female",
        )

        self.assertEqual(str(patient), "1 - Muster, Anna")

class PatientApiTest(APITestCase):
    def test_create_patient(self):
        response = self.client.post(
            "/api/patients/",
            {
                "first_name": "Max",
                "last_name": "Mustermann",
                "sex": "male",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Patient.objects.count(), 1)

    def test_list_patients(self):
        Patient.objects.create(
            first_name="Lisa",
            last_name="Beispiel",
            sex="female",
        )

        response = self.client.get("/api/patients/")

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)
