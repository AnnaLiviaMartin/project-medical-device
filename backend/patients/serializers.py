# patients/serializers.py
from datetime import date
from rest_framework import serializers
from .models import Patient, Allergy, Medication, HistoryEntry, Attachment


def calculate_age(birth_date):
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ["name", "dosage", "schedule"]


class PatientListSerializer(serializers.ModelSerializer):
    """Format für die Übersicht (/api/patients/)"""
    name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    gender = serializers.CharField(source="sex")
    address = serializers.SerializerMethodField()
    emergencyContact = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            "id", "name", "age", "gender", "diagnosis", "status",
            "doctor", "ward", "address", "emergencyContact",
        ]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_age(self, obj):
        return calculate_age(obj.date_of_birth)

    def get_address(self, obj):
        return {"street": obj.address_street, "zip": obj.address_zip, "city": obj.address_city}

    def get_emergencyContact(self, obj):
        return {
            "name": obj.emergency_contact_name,
            "relation": obj.emergency_contact_relation,
            "phone": obj.emergency_contact_phone,
        }


class PatientDetailSerializer(serializers.ModelSerializer):
    """Vollständiges Format für einen einzelnen Patienten (/api/patients/{id}/)"""
    name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    gender = serializers.CharField(source="sex")
    lastVisit = serializers.DateField(source="last_visit", format="%d.%m.%Y")
    nextAppointment = serializers.DateField(source="next_appointment", format="%d.%m.%Y")

    address = serializers.SerializerMethodField()
    emergencyContact = serializers.SerializerMethodField()
    insurance = serializers.SerializerMethodField()
    vitals = serializers.SerializerMethodField()

    allergies = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    medications = MedicationSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id", "name", "age", "gender", "diagnosis", "status",
            "lastVisit", "nextAppointment", "doctor", "ward",
            "address", "emergencyContact", "insurance",
            "allergies", "medications", "vitals",
        ]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_age(self, obj):
        return calculate_age(obj.date_of_birth)

    def get_address(self, obj):
        return {"street": obj.address_street, "zip": obj.address_zip, "city": obj.address_city}

    def get_emergencyContact(self, obj):
        return {
            "name": obj.emergency_contact_name,
            "relation": obj.emergency_contact_relation,
            "phone": obj.emergency_contact_phone,
        }

    def get_insurance(self, obj):
        return {"provider": obj.insurance_provider, "policyNumber": obj.insurance_policy_number}

    def get_vitals(self, obj):
        return {
            "bloodPressure": obj.vitals_blood_pressure,
            "heartRate": obj.vitals_heart_rate,
            "oxygenSaturation": obj.vitals_oxygen_saturation,
            "temperature": obj.vitals_temperature,
        }


    
class PatientCreateSerializer(serializers.ModelSerializer):
    allergies = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    medications = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )

    class Meta:
        model = Patient
        fields = [
            "id",
            "first_name", "last_name", "date_of_birth", "sex",
            "diagnosis", "status", "last_visit", "next_appointment",
            "doctor", "ward",
            "address_street", "address_zip", "address_city",
            "emergency_contact_name", "emergency_contact_relation", "emergency_contact_phone",
            "insurance_provider", "insurance_policy_number",
            "vitals_blood_pressure", "vitals_heart_rate",
            "vitals_oxygen_saturation", "vitals_temperature",
            "allergies", "medications",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        allergies_data = validated_data.pop("allergies", [])
        medications_data = validated_data.pop("medications", [])
        patient = Patient.objects.create(**validated_data)

        for allergy_name in allergies_data:
            Allergy.objects.create(patient=patient, name=allergy_name)

        for med in medications_data:
            Medication.objects.create(
                patient=patient,
                name=med.get("name", ""),
                dosage=med.get("dosage", ""),
                schedule=med.get("schedule", ""),
            )

        return patient
    
class AttachmentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    url = serializers.SerializerMethodField()
    fileName = serializers.SerializerMethodField()
    fileSize = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ["id", "history_entry", "file", "url", "fileName", "fileSize", "uploaded_at"]
        read_only_fields = ["id", "history_entry", "uploaded_at"]

    def get_url(self, obj):
        request = self.context.get("request")
        if request and obj.file:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None

    def get_fileName(self, obj):
        return obj.original_filename or (obj.file.name if obj.file else "")

    def get_fileSize(self, obj):
        try:
            return obj.file.size if obj.file else 0
        except Exception:
            return 0
        

class HistoryEntrySerializer(serializers.ModelSerializer):
    scans = serializers.SerializerMethodField()
    attachments = AttachmentSerializer(many=True, read_only=True)
    analysis = serializers.SerializerMethodField()

    class Meta:
        model = HistoryEntry
        fields = [
            "id", "patient", "study", "date", "title", "category",
            "description", "doctor", "department", "scans", "attachments",
            "analysis",
        ]
        read_only_fields = ["id"]

    def get_scans(self, obj):
        if not obj.study:
            return []
        request = self.context.get("request")
        result = []
        for img in obj.study.xray_images.all():
            url = img.image.url
            if request:
                url = request.build_absolute_uri(url)
            result.append({
                "id": img.id,
                "title": "Chest X-Ray",
                "date": img.uploaded_at.strftime("%d.%m.%Y"),
                "modality": "X-Ray",
                "href": url,
            })
        return result

    def get_analysis(self, obj):
        if not obj.study:
            return None

        image = obj.study.xray_images.order_by("-uploaded_at").first()
        if not image:
            return None

        prediction = getattr(image, "prediction", None)
        if not prediction:
            return None

        request = self.context.get("request")

        def to_absolute(relative_media_path):
            from django.conf import settings
            url = settings.MEDIA_URL + relative_media_path
            return request.build_absolute_uri(url) if request else url

        image_url = image.image.url
        if request:
            image_url = request.build_absolute_uri(image_url)

        raw_result = prediction.raw_result or {}
        positive_findings = raw_result.get("positive_findings", {})
        gradcam_paths = raw_result.get("gradcam_paths", {})

        if positive_findings:
            findings = [
                {
                    "title": pathology,
                    "text": f"Wahrscheinlichkeit fuer {pathology} liegt bei {round(score * 100, 1)}%.",
                    "disease": pathology,
                    "confidence": round(score * 100, 1),
                    "gradCamSrc": to_absolute(gradcam_paths[pathology]) if pathology in gradcam_paths else None,
                }
                for pathology, score in positive_findings.items()
            ]
        else:
            findings = [
                {
                    "title": "No Finding",
                    "text": "Keine auffälligen Befunde erkannt.",
                    "confidence": round(prediction.confidence * 100, 1),
                }
            ]

        return {
            "imageSrc": image_url,
            "title": "Chest X-Ray Analysis",
            "engine": "AI Model v1",
            "status": "No Finding" if not positive_findings else "Findings Detected",
            "confidence": round(prediction.confidence * 100, 1),
            "score": round(prediction.confidence * 100, 1),
            "findings": findings,
        }