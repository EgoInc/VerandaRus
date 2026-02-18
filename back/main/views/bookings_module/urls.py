from django.urls import path
from .views import BookingCancelView, BookingCreateView, BookingDetailView

urlpatterns = [
    path("", BookingCreateView.as_view(), name="booking-create"),
    path("<uuid:pk>/", BookingDetailView.as_view(), name="booking-detail"),
    path("<uuid:pk>/cancel/", BookingCancelView.as_view(), name="booking-cancel"),
]
