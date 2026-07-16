from rest_framework.routers import DefaultRouter
from .views import XRayImageViewSet

router = DefaultRouter()
router.register(r"images", XRayImageViewSet, basename="image")

urlpatterns = router.urls