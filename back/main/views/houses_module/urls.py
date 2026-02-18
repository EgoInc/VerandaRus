from django.urls import path
from .views import AccommodationAvailabilityView, HousesListView

urlpatterns = [
    path("", HousesListView.as_view(), name="houses-list"),
    path(
        "<uuid:pk>/availability/",
        AccommodationAvailabilityView.as_view(),
        name="accommodation-availability",
    ),
]
