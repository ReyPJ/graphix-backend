from django.urls import path
from .views import StageDataView, FileUploadView


urlpatterns = [
    path("save-stage/", StageDataView.as_view(), name="save-stage"),
    path("upload-images/", FileUploadView.as_view(), name="upload-images"),
]
