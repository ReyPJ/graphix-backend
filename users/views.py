from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import CustomUser
from .serializers import TemporaryUserSerializer


class TemporaryUserCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.filter(is_temporary=True)
    serializer_class = TemporaryUserSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        response_data = response.data
        return Response(
            {
                "id": response_data["id"],
                "username": response_data["username"],
                "password": response_data["raw_password"],
                "package": response_data["package"],
                "page_limit": response_data["page_limit"],
                "pdf_progress": response_data["pdf_progress"],
            },
            status=201,
        )


class GetUserListView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(is_temporary=True)
    serializer_class = TemporaryUserSerializer
    permission_classes = [IsAuthenticated]


class GetUserInfoView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = TemporaryUserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(user)

        return Response(serializer.data, status=200)


class DeleteUserView(generics.DestroyAPIView):
    queryset = CustomUser.objects.filter(is_temporary=True)
    serializer_class = TemporaryUserSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        userIds = request.data.get("userIds", [])

        if not userIds:
            return Response({"detail": "No user IDs provided"}, status=400)

        users_to_delete = CustomUser.objects.filter(id__in=userIds, is_temporary=True)
        if users_to_delete.exists():
            count, _ = users_to_delete.delete()
            return Response(
                {"message": f"{count} usuarios eliminados correctamente"}, status=204
            )

        return Response(
            {"detail": "No users found with the provided IDs."},
            status=404,
        )
