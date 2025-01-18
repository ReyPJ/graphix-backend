from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    is_temporary = models.BooleanField(default=False)
    package = models.CharField(
        max_length=20,
        choices=[("basic", "Basico"), ("medium", "Medio"), ("premium", "Premium")],
        null=True,
        blank=True,
    )
    pdf_progress = models.IntegerField(default=1)
    page_limit = models.IntegerField(default=50)

    raw_password = models.CharField(max_length=250, editable=False)

    def set_page_limit(self):
        if self.package == "basic":
            self.page_limit = 50

        elif self.package == "medium":
            self.page_limit = 150

        elif self.package == "premium":
            self.page_limit = 250

        self.save()
