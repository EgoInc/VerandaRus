from django.urls import path
from .views import MyBookingsView, BlacklistCreateView, DevLoginView, AuthorizationView

urlpatterns = [
    path("me/bookings/", MyBookingsView.as_view(), name="my-bookings"),
    path("blacklist/", BlacklistCreateView.as_view(), name="blacklist-create"),
    path("auth/", AuthorizationView.as_view(), name="authorization"),
    path("auth/dev-login/", DevLoginView.as_view(), name="dev-login"),
]
