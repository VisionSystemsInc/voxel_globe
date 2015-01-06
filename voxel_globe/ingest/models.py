from django.db import models

# Create your models here.

#key: [Friendly name, moduleName]
#Module name should not includ tasks, but it is assume that tasks.ingest_data is used
#I'm sure this will be updated at a later time to have api data in the module rather than here 
SENSOR_TYPES = {'arducopter':['Arducopter', 'voxel_globe.arducopter'], 
                'jpg_exif':['JPEG with EXIF tags', 'voxel_globe.jpg_exif']};
#to be used in conjunction with importlib

class IngestCommonModel(models.Model):
  class Meta:
    abstract = True
  name = models.TextField();
  owner = models.ForeignKey('auth.user');

  def __unicode__(self):
    return '%s[%s]: %s' % (self.name, self.id, self.owner.username)

class UploadSession(IngestCommonModel):
  sensorType = models.CharField(max_length=30)
  pass;

class Directory(IngestCommonModel):
  session = models.ForeignKey('UploadSession', related_name='directory');

class File(IngestCommonModel):
  directory = models.ForeignKey('Directory', related_name='file');
  completed = models.BooleanField(default=False);
