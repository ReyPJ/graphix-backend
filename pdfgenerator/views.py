from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import GeneratePDFSerializer
from .models import GeneratedPDFModel
from weasyprint import HTML
from django.conf import settings
import os
from pdf2image import convert_from_path


class GeneratePreviewsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GeneratePDFSerializer

    def post(self, request):
        """
        Genera vistas previas de las etapas del PDF.
        """
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        stages = serializer.validated_data["stages"]

        if sum(stage["page_count"] for stage in stages) > user.page_limit:
            return Response(
                {"error": "The total number of pages exceeds your limit."}, status=400
            )

        try:
            preview_image_paths = []

            # Para cada etapa, generar un archivo PDF temporal y convertirlo a imagen (primera página)
            for stage_index, stage in enumerate(stages):
                html = HTML(string=stage["html"])
                stage_pdf_path = os.path.join(
                    settings.TEMP_PDF_ROOT,
                    f"{user.username}_stage_{stage_index + 1}_temp.pdf",
                )
                html.write_pdf(stage_pdf_path)

                # Convertir el PDF a una imagen de la primera página
                images = convert_from_path(stage_pdf_path, first_page=1, last_page=1)

                # Guardar la imagen generada en formato PNG (solo la primera página)
                preview_image_path = os.path.join(
                    settings.PREVIEW_IMAGES_ROOT, f"{user.username}_stage_{stage_index + 1}_preview.png"
                )
                images[0].save(preview_image_path, "PNG")
                preview_image_paths.append(preview_image_path)

                # Eliminar el archivo PDF temporal después de convertirlo
                os.remove(stage_pdf_path)

            return Response(
                {
                    "message": "Preview images generated successfully.",
                    "preview_images": preview_image_paths,
                }
            )

        except Exception as e:
            return Response(
                {"error": f"Error generating previews: {str(e)}"}, status=500
            )


class ConfirmAndGeneratePDFView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GeneratePDFSerializer

    def post(self, request):
        """
        Genera el PDF final después de confirmar las vistas previas.
        """
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        stages = serializer.validated_data["stages"]
        cover_image = serializer.validated_data.get("cover_image")
        confirm = request.data.get("confirm", False)

        if not confirm:
            return Response(
                {"error": "You must confirm the preview before generating the PDF."},
                status=400,
            )

        temp_pdf_path = os.path.join(settings.TEMP_PDF_ROOT, f"{user.username}.pdf")

        try:
            combined_html_content = ""

            if cover_image:
                combined_html_content += f"""
                <div style="text-align: center; margin: 50px 0;">
                    <img src="{cover_image}" style="width: 100%; height: auto;" alt="Cover Image" />
                </div>
                <div style="page-break-before: always;"></div>
                """

            for stage in stages:
                # Dividir la etapa en tantas partes como lo indique page_count
                page_count = stage["page_count"]
                stage_html = stage["html"]

                # Si el page_count es mayor a 1, duplicamos el contenido de la etapa
                # Para cada página en la etapa, añadimos el mismo contenido HTML.
                for i in range(page_count):
                    stage_page_html = f"""
                    <div>{stage_html}</div>
                    <div style="page-break-before: always;"></div>
                    """
                    combined_html_content += stage_page_html

            # Generamos el PDF a partir del contenido combinado
            html = HTML(string=combined_html_content)
            pdf_content = html.write_pdf()

            # Guardar el PDF generado en un archivo
            with open(temp_pdf_path, "wb") as pdf_file:
                pdf_file.write(pdf_content)

            # Guardar el modelo y progreso del usuario
            GeneratedPDFModel.objects.create(user=user, pdf_file=temp_pdf_path)

            # Eliminar el usuario temporal si aplica
            if user.is_temporary:
                user.delete()

            return Response(
                {"message": "PDF generated successfully.", "pdf_path": temp_pdf_path}
            )

        except Exception as e:
            return Response({"error": f"Error generating PDF: {str(e)}"}, status=500)
