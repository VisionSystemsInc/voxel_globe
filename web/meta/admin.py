from django.contrib import admin
from meta.models import *

# Register your models here.
admin.site.register(Image)
admin.site.register(ImageTiePoint)
admin.site.register(GeoTiePoint)

class ServiceInstanceAdmin(admin.ModelAdmin):
  list_display = ('__unicode__', 'entryTime', 'finishTime', 'inputs', 'outputs');
admin.site.register(ServiceInstance, ServiceInstanceAdmin)
admin.site.register(WorkflowInstance)