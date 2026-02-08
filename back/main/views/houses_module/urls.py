from django.urls import path
from .views import HousesListView

urlpatterns = [
    path("", HousesListView.as_view(), name="houses-list"),
]
