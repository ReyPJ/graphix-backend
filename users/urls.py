from django.urls import path
from .views import TemporaryUserCreateView, GetUserInfoView

urlpatterns = [
    path(
        "create-user/",
        TemporaryUserCreateView.as_view(),
        name="create a temporary user",
    ),
    path("get-user/<int:pk>/", GetUserInfoView.as_view(), name="user info")
]
