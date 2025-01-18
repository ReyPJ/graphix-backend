from django.db import models
from users.models import CustomUser


class StageDataModel(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="stages"
    )
    stage_number = models.IntegerField()
    html = models.TextField(blank=True, null=True)
    page_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
