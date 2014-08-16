from django.contrib import admin
import meta.models;

import django.forms.widgets
import django.contrib.gis.forms.widgets

import django.contrib.gis.db.models

import inspect

''' Non-VIPObjectModels ''' 
admin.site.register(meta.models.WorkflowInstance)
class ServiceInstanceAdmin(admin.ModelAdmin):
  list_display = ('__unicode__', 'entryTime', 'finishTime', 'inputs', 'outputs');
admin.site.register(meta.models.ServiceInstance, ServiceInstanceAdmin)

''' Custom VipObjectModels ''' 
class TiePointAdmin(admin.ModelAdmin):
  formfield_overrides = {django.contrib.gis.db.models.PointField: {'widget': django.forms.widgets.TextInput }};
admin.site.register(meta.models.TiePoint, TiePointAdmin)

class ControlPointAdmin(admin.ModelAdmin):
  formfield_overrides = {django.contrib.gis.db.models.PointField: {'widget': django.contrib.gis.forms.widgets.OSMWidget }};
admin.site.register(meta.models.ControlPoint, ControlPointAdmin)

''' Register EVERYTHING else '''
for m in inspect.getmembers(meta.models):
   try:
    if issubclass(m[1], meta.models.VipObjectModel):
      admin.site.register(m[1]);
   except:
     pass 