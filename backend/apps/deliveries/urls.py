from rest_framework.routers import DefaultRouter
from .views import DeliveryAttemptViewSet


router = DefaultRouter()
router.register(
    "deliveries",
    DeliveryAttemptViewSet,
    basename="delivery-attempt",
)

urlpatterns = router.urls