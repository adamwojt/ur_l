from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from rest_framework import serializers

from .apps import ApiConfig as conf
from .helpers import check_and_update_url_schema
from .models import Url


class UrlSerializer(serializers.Serializer):
    token = serializers.CharField(
        read_only=True, required=False, max_length=conf.TOKEN_LENGTH_STR
    )
    long_url = serializers.CharField(required=True, max_length=500)
    short_url = serializers.CharField(required=False, read_only=True, default="")
    click_count = serializers.IntegerField(required=False, read_only=True)
    click_limit = serializers.IntegerField(required=False)

    def validate_long_url(self, value):
        """
        First append schema if needed if still wrong
        raise rest_framework.serializers.ValidationError
        """
        long_url = check_and_update_url_schema(value)
        try:
            URLValidator()(long_url)
        except ValidationError:
            raise serializers.ValidationError("Wrong url given")
        else:
            return long_url

    def create(self, validated_data):
        return Url.objects.create_short_url(
            validated_data["long_url"], click_limit=validated_data.get("click_limit")
        )

    def update(self, instance, validated_data):
        instance.long_url = validated_data["long_url"]
        instance.save()
        return instance
