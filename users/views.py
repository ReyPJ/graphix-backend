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
            }
        )


class GetUserInfoView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = TemporaryUserSerializer
    permission_classes = [IsAuthenticated]
