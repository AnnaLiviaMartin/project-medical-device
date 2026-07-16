import os
from django.core.management.base import BaseCommand
from patients.models import Patient
from imaging.models import Study, XRayImage
from ml.models import Prediction


class Command(BaseCommand):
    help = "Löscht alle gespeicherten Daten und Bilddateien"

    def handle(self, *args, **options):
        deleted_files = 0

        # 1) Bilddateien löschen
        for image in XRayImage.objects.all():
            try:
                if image.image and hasattr(image.image, "path"):
                    file_path = image.image.path
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        deleted_files += 1
            except Exception as exc:
                self.stdout.write(self.style.WARNING(
                    f"Konnte Datei für Bild {image.id} nicht löschen: {exc}"
                ))

        # 2) Datenbankeinträge löschen
        # Reihenfolge: erst abhängige Objekte, dann Elternobjekte
        Prediction.objects.all().delete()
        XRayImage.objects.all().delete()
        Study.objects.all().delete()
        Patient.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(
            f"Alle Daten wurden gelöscht. Gelöschte Dateien: {deleted_files}"
        ))
