import meta.models

from rest_framework import serializers

class ImageSerializer(serializers.ModelSerializer):
  class Meta:
    model = meta.models.Image