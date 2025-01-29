from rest_framework.views import APIView
from django.core.files.storage import default_storage
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import GeneratePDFSerializer
from .models import GeneratedPDFModel
from weasyprint import HTML
import hashlib
from pdf2image import convert_from_path
import tempfile
import os


class GeneratePreviewsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GeneratePDFSerializer

    def post(self, request):
        """
        Genera vistas previas de las etapas del PDF usando almacenamiento en la nube
        """
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        stages = serializer.validated_data["stages"]

        try:
            # Generar contenido combinado y hash único
            combined_html = "\n".join(
                [f'<div class="page">{stage["html"]}</div>' for stage in stages]
            )
            content_hash = hashlib.sha256(combined_html.encode("utf-8")).hexdigest()[
                :10
            ]
            preview_image_urls = []

            # Verificar si existen las imágenes en el almacenamiento
            all_images_exist = True
            for page_number in range(1, len(stages) + 1):
                filename = (
                    f"{user.username}_{content_hash}_stage_{page_number}_preview.png"
                )
                filepath = f"preview_images/{filename}"

                if not default_storage.exists(filepath):
                    all_images_exist = False
                    break

                preview_image_urls.append(default_storage.url(filepath))

            if all_images_exist:
                return Response(
                    {
                        "message": "Preview images retrieved from cache.",
                        "preview_images": preview_image_urls,
                    }
                )

            # Generar nuevo PDF temporal
            css = """
            <style>
                @page { size: A4; margin: 1cm; }
                .page { page-break-after: always; }
                .page:last-child { page-break-after: auto; }
            </style>
            """
            full_html = f"{css}{combined_html}"
            html = HTML(string=full_html)

            # Crear archivo temporal para la conversión
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
                pdf_content = html.write_pdf()
                tmp_pdf.write(pdf_content)
                tmp_pdf_path = tmp_pdf.name

            # Convertir a imágenes desde el archivo temporal
            images = convert_from_path(tmp_pdf_path)
            os.unlink(tmp_pdf_path)  # Eliminar archivo temporal

            # Guardar imágenes en el almacenamiento en la nube
            preview_image_urls = []
            for page_number, image in enumerate(images, start=1):
                filename = (
                    f"{user.username}_{content_hash}_stage_{page_number}_preview.png"
                )
                filepath = f"preview_images/{filename}"

                # Guardar imagen directamente en el almacenamiento
                with tempfile.NamedTemporaryFile(suffix=".png") as tmp_img:
                    image.save(tmp_img.name, "PNG")
                    default_storage.save(filepath, tmp_img)

                preview_image_urls.append(default_storage.url(filepath))

            return Response(
                {
                    "message": "Preview images generated successfully.",
                    "preview_images": preview_image_urls,
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class ConfirmAndGeneratePDFView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GeneratePDFSerializer

    def post(self, request):
        """
        Genera el PDF final y lo guarda en el object storage
        """
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        stages = serializer.validated_data["stages"]
        confirm = request.data.get("confirm", False)

        if not confirm:
            return Response(
                {"error": "Debes confirmar la vista previa antes de generar el PDF."},
                status=400,
            )

        try:
            combined_html_content = ""
            for stage in stages:
                page_count = stage["page_count"]
                stage_html = stage["html"]

                for _ in range(page_count):
                    combined_html_content += f"""
                    <div>{stage_html}</div>
                    <div style="page-break-before: always;"></div>
                    """

            # Generar PDF
            html = HTML(string=combined_html_content)
            pdf_content = html.write_pdf()

            # Guardar directamente en el object storage
            filename = f"{user.username}_final.pdf"
            filepath = f"final_pdfs/{filename}"

            with tempfile.NamedTemporaryFile() as tmp_file:
                tmp_file.write(pdf_content)
                tmp_file.flush()
                default_storage.save(filepath, tmp_file)

            # Registrar en la base de datos
            GeneratedPDFModel.objects.create(user=user, pdf_file=filepath)

            # Eliminar usuario temporal si aplica
            if hasattr(user, "is_temporary") and user.is_temporary:
                user.delete()

            return Response(
                {
                    "message": "PDF generado exitosamente.",
                    "pdf_url": default_storage.url(filepath),
                }
            )

        except Exception as e:
            return Response({"error": f"Error generando PDF: {str(e)}"}, status=500)
