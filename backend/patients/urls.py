from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, HistoryEntryViewSet, AttachmentViewSet
from imaging.views import HistoryScanUploadView

router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patient")
router.register(r"history", HistoryEntryViewSet, basename="history")

attachment_list = AttachmentViewSet.as_view({"get": "list", "post": "create"})
attachment_detail = AttachmentViewSet.as_view({"delete": "destroy"})

urlpatterns = router.urls + [
    path(
        "patients/<int:patient_id>/history/<int:entry_id>/attachments/",
        attachment_list,
        name="attachment-list",
    ),
    path(
        "patients/<int:patient_id>/history/<int:entry_id>/attachments/<int:pk>/",
        attachment_detail,
        name="attachment-detail",
    ),
    path(
        "patients/<int:patient_id>/history/<int:entry_id>/scans/",
        HistoryScanUploadView.as_view(),
        name="history-scan-upload",
    ),
]