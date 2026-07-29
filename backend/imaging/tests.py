from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APITestCase
from patients.models import Patient
from .models import Study, XRayImage
from ml.models import Prediction

class StudyModelTest(TestCase):
    def test_study_creation(self):
        patient = Patient.objects.create(
            first_name="Anna",
            last_name="Muster",
            sex="female",
        )

        study = Study.objects.create(patient=patient)

        self.assertEqual(study.patient, patient)
        self.assertIsNotNone(study.created_at)

class XRayImageModelTest(TestCase):
    def test_xray_image_creation(self):
        patient = Patient.objects.create(
            first_name="Ben",
            last_name="Tester",
            sex="male",
        )
        study = Study.objects.create(patient=patient)

        fake_file = SimpleUploadedFile(
            "test_xray.png",
            b"fake-image-content",
            content_type="image/png",
        )

        image = XRayImage.objects.create(
            study=study,
            image=fake_file,
        )

        self.assertEqual(image.study, study)
        self.assertEqual(image.prediction_status, "pending")

class StudyApiTest(APITestCase):
    def test_create_study(self):
        patient = Patient.objects.create(
            first_name="Clara",
            last_name="Beispiel",
            sex="female",
        )

        response = self.client.post(
            "/api/studies/",
            {"patient": patient.id},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Study.objects.count(), 1)

class XRayImageUploadApiTest(APITestCase):
    def test_upload_image(self):
        patient = Patient.objects.create(
            first_name="David",
            last_name="Upload",
            sex="male",
        )
        study = Study.objects.create(patient=patient)

        fake_file = SimpleUploadedFile(
            "test_xray.png",
            b"fake-image-content",
            content_type="image/png",
        )

        response = self.client.post(
            "/api/images/",
            {
                "study": study.id,
                "image": fake_file,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(XRayImage.objects.count(), 1)

class XRayInferenceApiTest(APITestCase):
    @patch("imaging.views.run_model_on_image")
    def test_upload_triggers_prediction(self, mock_run_model):
        mock_run_model.return_value = {
            "label": "normal",
            "confidence": 0.93,
            "raw": {
                "model_version": "v1"
            },
        }

        patient = Patient.objects.create(
            first_name="Eva",
            last_name="Inference",
            sex="female",
        )
        study = Study.objects.create(patient=patient)

        fake_file = SimpleUploadedFile(
            "test_xray.png",
            b"fake-image-content",
            content_type="image/png",
        )

        response = self.client.post(
            "/api/images/",
            {
                "study": study.id,
                "image": fake_file,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(XRayImage.objects.count(), 1)
        self.assertEqual(Prediction.objects.count(), 1)

        image = XRayImage.objects.first()
        self.assertEqual(image.prediction_status, "done")
        mock_run_model.assert_called_once()
