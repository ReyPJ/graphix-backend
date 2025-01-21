from django.urls import path
from .views import StageDataView, FileUploadView


urlpatterns = [
    path("save-stage/", StageDataView.as_view(), name="save-stage"),
    path("upload-cover-image/", FileUploadView.as_view(), name="upload-cover"),
]
