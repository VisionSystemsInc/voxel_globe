import meta.models

from rest_framework import serializers
from rest_framework_gis import serializers as serializers_gis

class VipModelSerializer(serializers_gis.GeoModelSerializer):
  def save_object(self, obj, **kwargs):
    #Turn save into HISTORY save, AKA update.
    kwargs.pop('force_update', None);
    #This is something rest_framework adds for the update, but
    #Given the nature of how I update, this is not needed.
    obj.update(**kwargs)

def serializerFactory(model):
  return type('AutoSerializer_%s' % model._meta.model_name, (VipModelSerializer,), {'Meta': type('AutoMeta',  (object,), {'model':model})})

class TiePointSerializer(serializers_gis.GeoModelSerializer):
  class Meta:
    model = meta.models.TiePoint;
  
#Define custom serializers here