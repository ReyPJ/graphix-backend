from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("token/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh_view"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify_view"),
    # users urls
    path("api/users/", include("users.urls")),
    # Documentation
    path("api/docs/", SpectacularAPIView.as_view(), name="docs"),
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name='docs'), name='swagger-docs'),
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name='docs'), name='redoc-docs'),
    # PDF generator
    path("api/pdf/", include("pdfgenerator.urls")),
    # Stages Backup
    path("api/pdf/save/", include("stages.urls")),
]
