from django.urls import path
from .views import GeneratePreviewsView, ConfirmAndGeneratePDFView

urlpatterns = [
    path("generate-previews/", GeneratePreviewsView.as_view(), name="generate-previews"),
    path("confirm-generate-pdf/", ConfirmAndGeneratePDFView.as_view(), name="confirm-generate-pdf"),
]
