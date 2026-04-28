from rest_framework.routers import DefaultRouter
from .views import EventReplayViewSet


router = DefaultRouter()
router.register("replays", EventReplayViewSet, basename="replay")

urlpatterns = router.urls