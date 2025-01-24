from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


def validate_non_negative(value):
    if value < 0:
        raise ValidationError("The value can't be negative'")


class CustomUser(AbstractUser):
    is_temporary = models.BooleanField(default=False)
    package = models.CharField(
        max_length=20,
        choices=[
            ("basic", "Basico"),
            ("medium", "Medio"),
            ("premium", "Premium"),
            ("gold", "Oro"),
            ("platinum", "Platino"),
            ("diamond", "Diamante"),
            ("custom", "Personalizado"),
        ],
        null=True,
        blank=True,
    )
    pdf_progress = models.IntegerField(default=1)
    page_limit = models.IntegerField(default=50, validators=[validate_non_negative])

    raw_password = models.CharField(max_length=250, editable=False)

    PACKAGE_PAGE_LIMITS = {
        "basic": 54,
        "medium": 64,
        "premium": 80,
        "gold": 90,
        "platinum": 100,
        "diamond": 150,
    }

    def set_page_limit(self):
        if self.package == "custom":
            return

        self.page_limit = self.PACKAGE_PAGE_LIMITS.get(self.package, 50)
        self.save()

    def clean(self):
        super().clean()

        if (
            self.package != "custom"
            and self.page_limit != self.PACKAGE_PAGE_LIMITS.get(self.package, 50)
        ):
            raise ValidationError(
                f"Limit of pages for package '{self.package}' needs to be {self.PACKAGE_PAGE_LIMITS.get(self.package, 50)}"
            )
