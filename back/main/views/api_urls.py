from django.urls import include, path

urlpatterns = [
    path("houses/", include("main.views.houses_module.urls")),
    path("bookings/", include("main.views.bookings_module.urls")),
    path("", include("main.views.users_module.urls")),
    path("", include("main.views.system_module.urls")),
]
