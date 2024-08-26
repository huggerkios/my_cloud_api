from django.urls import path, include

urlpatterns = [
    path("admin/", include("apps.administration.urls")),
    path("cloud/", include("apps.cloud.urls")),
]
