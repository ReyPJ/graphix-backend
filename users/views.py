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


class PdfProgressUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.filter(is_temporary=True)
    serializer_class = TemporaryUserSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        pdf_progress = request.data.get("pdf_progress", user.pdf_progress)

        if pdf_progress < 0 or pdf_progress > 5:
            return Response({"error": "El progreso debe ser entre 0 y 5"})

        user.pdf_progress = pdf_progress

        user.save()
        return Response({"id": user.id, "pdf_progress": user.pdf_progress})
