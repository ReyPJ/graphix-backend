from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from weasyprint import HTML
from django.conf import settings
import os


class GeneratePDFView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        TODO: Terminar la vista que acepte codigo HTML, CSS e Imagenes
        como body de la request y convertirlo a un pdf con weasyprint
        de forma ordenada y justo como necesitamos que sea convertido.
        """
        pass
