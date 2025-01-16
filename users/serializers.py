from rest_framework import serializers
from .models import CustomUser
from django.utils.crypto import get_random_string


class TemporaryUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "password",
            "is_temporary",
            "pdf_progress",
            "package",
            "page_limit",
            "raw_password",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password", get_random_string(8))

        user = CustomUser.objects.create(
            **validated_data, password=password
        )
        user.set_page_limit()
        user.raw_password = password
        user.set_password(password)
        user.save()

        return user

    def update(self, instance, validated_data):
        instance.pdf_progress = validated_data.get(
            "pdf_progress", instance.pdf_progress
        )
        instance.save()
        return instance
