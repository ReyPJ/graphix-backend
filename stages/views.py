from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import StageSerializer
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
