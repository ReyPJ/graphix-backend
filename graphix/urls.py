from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("token/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh_view"),
    # users urls
    path("api/users/", include("users.urls")),
    # Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger/", SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-schema'),
    # PDF generator
    path("api/pdf/", include("pdfgenerator.urls")),
    # Stages Backup
    path("api/pdf/save/", include("stages.urls")),
]
