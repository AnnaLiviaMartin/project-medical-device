# imaging/urls.py
from rest_framework.routers import DefaultRouter
from .views import StudyViewSet, XRayImageViewSet

router = DefaultRouter()
router.register(r"images", XRayImageViewSet, basename="image")
router.register(r"studies", StudyViewSet, basename="study")
urlpatterns = router.urls