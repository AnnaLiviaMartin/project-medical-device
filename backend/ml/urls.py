from django.urls import path
from .views import PredictionByImageView

urlpatterns = [
    path("images/<int:image_id>/prediction/", PredictionByImageView.as_view()),
]
