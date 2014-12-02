from django.db import models
import voxel_globe.meta.models
# Create your models here.

class Order(models.Model):
  processingDir = models.TextField()
  #imageCollection = models.ForeignKey('meta.ImageCollection', blank=False, null=False);
  lvcsOrigin = models.TextField()