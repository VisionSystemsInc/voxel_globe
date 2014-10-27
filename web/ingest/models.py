from django.db import models

# Create your models here.

class UploadSession(models.Model):
  name = models.TextField(); #Do I need this?
  owner = models.ForeignKey('auth.user');
  uploadId = models.CharField('Upload ID', max_length=36);
  
  def __unicode__(self):
    return '%s[%s,%s]' % (self.name, self.id, self.uploadId)

class Directory(models.Model):
  name = models.TextField();
  session = models.ForeignKey('UploadSession', related_name='directory');

  def __unicode__(self):
    return '%s[%s]' % (self.name, self.id)

class File(models.Model):
  filename = models.TextField();
  directory = models.ForeignKey('Directory', related_name='file');
  completed = models.BooleanField(default=False);

  def __unicode__(self):
    return '%s[%s]' % (self.filename, self.id)
