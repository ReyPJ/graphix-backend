from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import GeneratePDFSerializer
from .models import GeneratedPDFModel
from weasyprint import HTML
from django.conf import settings
import os
import hashlib
from pdf2image import convert_from_path


class GeneratePreviewsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GeneratePDFSerializer

    def post(self, request):
        """
        Genera vistas previas de las etapas del PDF solo si no existen previamente
        """
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        stages = serializer.validated_data["stages"]

        try:
            os.makedirs(settings.TEMP_PDF_ROOT, exist_ok=True)
            os.makedirs(settings.PREVIEW_IMAGES_ROOT, exist_ok=True)

            # Generar contenido combinado y hash único
            combined_html = "\n".join(
                [f'<div class="page">{stage["html"]}</div>' for stage in stages]
            )
            content_hash = hashlib.sha256(combined_html.encode("utf-8")).hexdigest()[
                :10
            ]
            base_url = request.build_absolute_uri("/")[:-1]
            preview_image_urls = []

            # Verificar si todas las imágenes ya existen
            all_images_exist = True
            for page_number in range(1, len(stages) + 1):
                filename = (
                    f"{user.username}_{content_hash}_stage_{page_number}_preview.png"
                )
                filepath = os.path.join(settings.PREVIEW_IMAGES_ROOT, filename)

                if not os.path.exists(filepath):
                    all_images_exist = False
                    break

                preview_image_urls.append(
                    f"{base_url}{settings.MEDIA_URL}preview_images/{filename}"
                )

            if all_images_exist:
                return Response(
                    {
                        "message": "Preview images retrieved from cache.",
                        "preview_images": preview_image_urls,
                    }
                )

            # Generar nuevo contenido si no existe
            css = """
            <style>
                @page { size: A4; margin: 1cm; }
                .page { page-break-after: always; }
                .page:last-child { page-break-after: auto; }
            </style>
            """
            full_html = f"{css}{combined_html}"
            html = HTML(string=full_html)

            # Generar PDF temporal con hash
            temp_pdf_path = os.path.join(
                settings.TEMP_PDF_ROOT, f"{user.username}_{content_hash}_temp.pdf"
            )
            html.write_pdf(temp_pdf_path)

            # Convertir a imágenes
            images = convert_from_path(temp_pdf_path)
            preview_image_urls = []

            for page_number, image in enumerate(images, start=1):
                filename = (
                    f"{user.username}_{content_hash}_stage_{page_number}_preview.png"
                )
                filepath = os.path.join(settings.PREVIEW_IMAGES_ROOT, filename)

                if not os.path.exists(filepath):
                    image.save(filepath, "PNG")

                preview_image_urls.append(
                    f"{base_url}{settings.MEDIA_URL}preview_images/{filename}"
                )

            return Response(
                {
                    "message": "Preview images generated successfully.",
                    "preview_images": preview_image_urls,
                }
            )

        except Exception as e:
            # Asegurar limpieza del PDF temporal en caso de error
            if "temp_pdf_path" in locals() and os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
            return Response({"error": str(e)}, status=500)


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
        confirm = request.data.get("confirm", False)

        if not confirm:
            return Response(
                {"error": "You must confirm the preview before generating the PDF."},
                status=400,
            )

        base_url = request.build_absolute_uri("/")[:-1]
        file_name = f"{user.username}.pdf"

        temp_pdf_path = os.path.join(settings.TEMP_PDF_ROOT, file_name)

        try:
            combined_html_content = ""

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
                {
                    "message": "PDF generated successfully.",
                    "pdf_path": f"{base_url}{temp_pdf_path}{file_name}",
                }
            )

        except Exception as e:
            return Response({"error": f"Error generating PDF: {str(e)}"}, status=500)
