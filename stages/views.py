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
from django.core.exceptions import ValidationError


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
                "userName": user.username,
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

        user.pdf_progress = stage_number + 1 if stage_number < 15 else 1
        if stage.page_count:
            if user.page_limit - stage.page_count < 0:
                raise ValidationError("Not enought pages avalible")
            user.page_limit -= stage.page_count

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

        if serializer.is_valid():
            files_urls = []
            for file in serializer.validated_data["files"]:
                # Sanitizar nombre de archivo
                clean_name = os.path.basename(file.name)

                # Ruta en el object storage (sin usar sistema de archivos local)
                file_key = f"resources_image/{clean_name}"

                # Guardar directamente en el object storage
                default_storage.save(file_key, file)

                # Obtener URL pública desde el storage
                files_urls.append(default_storage.url(file_key))

            return Response({"files_url": files_urls}, status=201)

        return Response(serializer.errors, status=400)
