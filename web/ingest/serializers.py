import meta.models

from rest_framework import serializers

def serializerFactory(model):
  return type('AutoSerializer_%s' % model._meta.model_name, (serializers.ModelSerializer,), 
              {'Meta': type('AutoMeta',  (object,), {'model':model})})
