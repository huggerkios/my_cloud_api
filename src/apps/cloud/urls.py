from django.urls import path

from .views import EmptyViewSet

urlpatterns = [path("", EmptyViewSet.as_view())]
