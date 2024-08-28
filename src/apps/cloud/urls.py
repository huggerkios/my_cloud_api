from django.urls import path, include

from rest_framework import routers

from .views import FileViewSet

router = routers.DefaultRouter()

router.register("files", FileViewSet, basename="files")

urlpatterns = [
    path(
        "files/share/<slug:uuid>/", FileViewSet.as_view({"get": "share"}), name="share"
    ),
    path("", include(router.urls)),
]
