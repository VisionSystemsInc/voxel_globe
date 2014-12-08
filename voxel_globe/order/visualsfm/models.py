from django.db import models
import voxel_globe.meta.models
# Create your models here.

class Order(models.Model):
  #no longer needed, mostly debugging
  processingDir = models.TextField()
  imageCollection = models.ForeignKey('meta.ImageCollection', blank=False, null=False);
  lvcsOrigin = models.TextField()
  
class Session(models.Model):
  owner = models.ForeignKey('auth.user', null=False, blank=False);
  uuid = models.CharField(max_length=36, null=False, blank=False);
  startTime = models.DateTimeField(auto_now_add = True);