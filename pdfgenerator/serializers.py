from rest_framework import serializers


class StageSerializer(serializers.Serializer):
    html = serializers.CharField(
        help_text="HTML content specific to this stage."
    )  # HTML para la etapa
    page_count = serializers.IntegerField(
        min_value=1,
        help_text="Number of pages allocated for this stage. Must be at least 1.",
    )  # Páginas de la etapa


class GeneratePDFSerializer(serializers.Serializer):
    stages = serializers.ListField(
        child=StageSerializer(),
        required=True,
        min_length=1,
        max_length=15,
        help_text="List of 15 or less stages. Each stage must have its own HTML and page count.",
    )  # Etapas individuales
    confirm = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Flag to confirm, if is true the PDF is gonna be downloaded and user deleted.",
    )

    def validate_stages(self, value):
        """
        Validate that the total number of pages in all stages is reasonable.
        """
        total_pages = sum(stage["page_count"] for stage in value)
        if total_pages <= 0:
            raise serializers.ValidationError(
                "Total page count across all stages must be greater than 0."
            )
        return value
