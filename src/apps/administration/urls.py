from django.urls import path, include

from rest_framework import routers

from .views import UserViewSet, AuthViewSet

router = routers.DefaultRouter()

router.register("auth", AuthViewSet, basename="auth")
router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
]
