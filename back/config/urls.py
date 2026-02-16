from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from main.views.users_module.views import BlacklistViewSet
from main.views.telegram_module.views import (
    LinkTelegramView, UnlinkTelegramView,
    TestNotificationView, DailyDigestView
)
router = DefaultRouter()
router.register(r'admin/blacklist', BlacklistViewSet, basename='blacklist')

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include(router.urls)),
    path("api/", include("main.views.api_urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path('api/me/telegram/link/', LinkTelegramView.as_view()),
    path('api/me/telegram/unlink/', UnlinkTelegramView.as_view()),
    path('api/admin/notifications/test/', TestNotificationView.as_view()),
    path('api/admin/notifications/daily/', DailyDigestView.as_view()),
]



