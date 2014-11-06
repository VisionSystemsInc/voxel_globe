from django.contrib import admin
import voxel_globe.meta.models;

import django.forms
import django.contrib.gis.forms.widgets

import django.contrib.gis.db.models

import inspect

def ModelLinkWidgetFactory(foreign_key):
  return type('TempModelLinkWidget', (ModelLinkWidget,), {'foreign_key':foreign_key})

class ModelLinkWidget(django.forms.Select):

    def __init__(self, attrs=None, choices=()):
        super(ModelLinkWidget,self).__init__(attrs, choices)

    def render(self, name, value, attrs=None, choices=()):
        if self.foreign_key is not None and value is not None:
          link = '&nbsp;&nbsp;&nbsp;Link:<a href="%s/%s/%s/%d">%d</a>' % ('/admin', #I don't know how to un hard code this
                               self.foreign_key.rel.to._meta.app_label, 
                               self.foreign_key.rel.to._meta.model_name,
                               value, value)
        else:
          link = "&nbsp;&nbsp;&nbsp;None"

        return super(ModelLinkWidget, self).render(name, value, attrs) + link;
                                                                
''' Non-VIPObjectModels ''' 
admin.site.register(voxel_globe.meta.models.WorkflowInstance)

def fk_link(self, obj):
  return '<a href="/admin/%s/%s/%d/">Link</a>' % (obj._meta.app_label, obj._meta.model_name, obj.pk)
fk_link.allow_tags = True
fk_link.short_description = "Link to object"

def history_link(self, obj):
  histories = obj._meta.model.objects.filter(objectId=obj.objectId)
  history_ids =  map(lambda x:x['id'], histories.values('id'))
  link_string = ''
  for id in history_ids:
    link_string += '<a href="/admin/%s/%s/%d/">%d</a><br>' % (obj._meta.app_label, obj._meta.model_name, id, id)
  return link_string
history_link.allow_tags = True
history_link.short_description = "Versions"

class VipInline(admin.TabularInline):
  template = 'admin/edit_inline/vip.html'
  fields = ('objectId', 'fk_link')
  extra = 0;
  readonly_fields=('objectId','fk_link')
  
  fk_link=fk_link;

def VipInlineFactory(model):
  return type(model._meta.model_name+'Inline', (VipInline,), {'model':model})

class ServiceInstanceAdmin(admin.ModelAdmin):
  list_display = ('__unicode__', 'entryTime', 'finishTime', 'inputs', 'outputs');
  inlines = [];

''' Custom VipObjectModels ''' 
class VipAdmin(admin.ModelAdmin):
  def formfield_for_dbfield(self, db_field, **kwargs):
    if isinstance(db_field, django.contrib.gis.db.models.ForeignKey):
      kwargs['widget'] = ModelLinkWidgetFactory(db_field)
      #This MAY explode, if EVERY instance is kept in memory, it's for dev only, so I'm ok with this
    return super(VipAdmin, self).formfield_for_dbfield(db_field, **kwargs);
  history_link = history_link;

  search_fields = ('name','objectId')

  readonly_fields=('history_link', 'service')
#  formfield_overrides = {django.contrib.gis.db.models.ForeignKey: {'widget':  ModelLinkWidget}};
  
class TiePointAdmin(VipAdmin):
  formfield_overrides = {django.contrib.gis.db.models.PointField: {'widget': django.forms.widgets.TextInput }};
admin.site.register(voxel_globe.meta.models.TiePoint, TiePointAdmin)

class CartesianTransformAdmin(VipAdmin):
  formfield_overrides = {django.contrib.gis.db.models.PointField: {'widget': django.forms.widgets.TextInput }};
  search_fields = ('name',) #Add this to all VIP?
admin.site.register(voxel_globe.meta.models.CartesianTransform, CartesianTransformAdmin)

class ControlPointAdmin(VipAdmin):
  formfield_overrides = {django.contrib.gis.db.models.PointField: {'widget': django.contrib.gis.forms.widgets.OSMWidget }};
admin.site.register(voxel_globe.meta.models.ControlPoint, ControlPointAdmin)

''' Register EVERYTHING else '''
for m in inspect.getmembers(voxel_globe.meta.models):
  ''' Add inlines for ALL VIP memebers '''
  try:
    if issubclass(m[1], voxel_globe.meta.models.VipObjectModel):
      if not admin.site._registry.has_key(voxel_globe.meta.models.Image):
        admin.site.register(m[1], VipAdmin);
  except (TypeError, admin.sites.AlreadyRegistered):
    pass 
  
  try:
    if issubclass(m[1], voxel_globe.meta.models.VipObjectModel) and not m[1] == voxel_globe.meta.models.VipObjectModel:
      ServiceInstanceAdmin.inlines.append(VipInlineFactory(m[1]))
  except:
    pass; 
admin.site.register(voxel_globe.meta.models.ServiceInstance, ServiceInstanceAdmin)
admin.site.register(voxel_globe.meta.models.History);
