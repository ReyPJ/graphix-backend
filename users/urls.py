from django.urls import path
from .views import TemporaryUserCreateView, GetUserListView, DeleteUserView, GetUserInfoView

urlpatterns = [
    path(
        "create-user/",
        TemporaryUserCreateView.as_view(),
        name="create a temporary user",
    ),
    path("get-users/", GetUserListView.as_view(), name="users-list"),
    path("delete-user/", DeleteUserView.as_view(), name="delete-user"),
    path("get-user-info/", GetUserInfoView.as_view(), name="get-user-info")
]
