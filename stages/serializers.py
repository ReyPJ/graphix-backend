from rest_framework import serializers
from .models import StageDataModel


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StageDataModel
        fields = "__all__"
        ref_name = "StageData"

    def validate_stage_number(self, value):
        if value < 1 or value > 15:
            raise serializers.ValidationError("Stage number must be between 1 and 15")
        return value


class FileSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False
    )
