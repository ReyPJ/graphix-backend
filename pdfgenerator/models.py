from django.db import models
from django.utils.timezone import now
from users.models import CustomUser
import os


def pdf_upload_path(instance, filename):
    return f'temp_pdfs/{instance.user.username}_{now().strftime("%d%m%Y%H%M%S")}.pdf'


class GeneratedPDFModel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    pdf_file = models.FileField(upload_to=pdf_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        if self.pdf_file:
            if os.path.isfile(self.pdf_file.path):
                os.remove(self.pdf_file.path)

        super().delete(*args, **kwargs)
