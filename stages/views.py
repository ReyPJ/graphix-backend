from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage
from django.conf import settings
import os
from .serializers import StageSerializer, FileSerializer
from .models import StageDataModel


class StageDataView(APIView):
    serializer_class = StageSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        stages = StageDataModel.objects.filter(user=user).order_by("stage_number")
        seralized_stages = StageSerializer(stages, many=True)

        return Response(
            {
                "pdf_progress": user.pdf_progress,
                "stages": seralized_stages.data,
                "userId": user.username,
            },
            status=200,
        )

    def post(self, request):
        user = request.user
        serializer = StageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        stage_number = serializer.validated_data["stage_number"]

        stage, created = StageDataModel.objects.update_or_create(
            user=user,
            stage_number=stage_number,
            defaults={
                "html": serializer.validated_data.get("html"),
                "page_count": serializer.validated_data.get("page_count"),
            },
        )

        user.pdf_progress = stage_number + 1 if stage_number < 6 else 1
        user.save()

        return Response(
            {
                "message": "Stage saved Succefully",
                "stage": StageSerializer(stage).data,
                "created": created,
            },
            status=201,
        )


class FileUploadView(GenericAPIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]
    serializer_class = FileSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data["file"]

        directory_path = settings.COVER_IMAGES_ROOT

        file_path = os.path.join(directory_path, file.name)
        with default_storage.open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Construir la URL del archivo
        file_url = os.path.join(settings.MEDIA_URL, "cover_images/", file.name)
        return Response({"file_url": request.build_absolute_uri(file_url)}, status=201)
