import io
import numpy as np
import pydicom
from PIL import Image
from django.core.files.base import ContentFile


def is_dicom_file(uploaded_file):
    name = getattr(uploaded_file, "name", "") or ""
    if name.lower().endswith(".dcm"):
        return True
    content_type = getattr(uploaded_file, "content_type", "") or ""
    return content_type in ("application/dicom", "application/octet-stream") and name.lower().endswith(".dcm")


def convert_dicom_to_png(uploaded_file):
    uploaded_file.seek(0)
    dataset = pydicom.dcmread(uploaded_file)
    pixel_array = dataset.pixel_array.astype(float)

    scaled = (np.maximum(pixel_array, 0) / pixel_array.max()) * 255.0
    scaled = np.uint8(scaled)

    image = Image.fromarray(scaled)
    if image.mode != "L":
        image = image.convert("L")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    original_name = getattr(uploaded_file, "name", "scan.dcm")
    new_name = original_name.rsplit(".", 1)[0] + ".png"

    return ContentFile(buffer.read(), name=new_name)