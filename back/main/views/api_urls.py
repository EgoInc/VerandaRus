from django.urls import include, path
from main.views.bookings_module.views import (
    AdminBookingListView,
    AdminBookingUpdateView,
)

urlpatterns = [
    path("accommodations/", include("main.views.houses_module.urls")),
    path("bookings/", include("main.views.bookings_module.urls")),
    path("", include("main.views.users_module.urls")),
    path("", include("main.views.system_module.urls")),
    path("admin/bookings/", AdminBookingListView.as_view(), name="admin-bookings-list"),
    path(
        "admin/bookings/<uuid:pk>/",
        AdminBookingUpdateView.as_view(),
        name="admin-bookings-update",
    ),
]
