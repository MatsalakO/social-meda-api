from rest_framework.routers import DefaultRouter

from social_media.views import (
    ProfileViewSet,
    PostViewSet,
)

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet)
router.register(r"posts", PostViewSet)


urlpatterns = router.urls

app_name = "social_media"
