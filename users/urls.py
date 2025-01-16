from django.urls import path
from .views import TemporaryUserCreateView, PdfProgressUpdateView

urlpatterns = [
    path(
        "create-user/",
        TemporaryUserCreateView.as_view(),
        name="create a temporary user",
    ),
    path(
        "update-progress/<int:pk>/",
        PdfProgressUpdateView.as_view(),
        name="update progress",
    ),
]
