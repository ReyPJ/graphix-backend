from django.urls import path
from .views import StageDataView


urlpatterns = [
    path("save-stage/", StageDataView.as_view(), name="save-stage"),
]
