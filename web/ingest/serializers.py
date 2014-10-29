from rest_framework import serializers

import ingest.models

class UploadSessionSerializer(serializers.ModelSerializer):
  #directory = serializers.RelatedField(many=True, read_only=True)
  class Meta(object):
    model = ingest.models.UploadSession;
    fields = ('id', 'name', 'directory')
    read_only_fields = ('directory',)

class DirectorySerializer(serializers.ModelSerializer):
  class Meta(object):
    model = ingest.models.Directory;
    fields = ('id', 'name', 'file', 'session')
    read_only_fields = ('file',)

class FileSerializer(serializers.ModelSerializer):
  class Meta:
    model = ingest.models.File;
    fields = ('id', 'name', 'directory', 'completed')

def NestFactory(serializer):
  return type('Nested', (serializer,), 
              {'Meta': type('Nested_Meta', (serializer.Meta,), {'depth':1})});