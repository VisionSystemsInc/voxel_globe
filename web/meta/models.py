from django.contrib.gis.db import models

# Create your models here.

PIXEL_FORMATS = (('f', 'Float'), ('d', 'Double'), ('q', 'Quadruple'), 
                 ('b', 'Byte 8'), ('s', 'Short 16'), 
                 ('i', 'Integer 32'), ('l', 'Long Integer 64'));

class Image(models.Model):
  name = models.CharField(max_length=128);
  fileFormat = models.CharField(max_length=4);
  pixelFormat =models.CharField(max_length=1, choices=PIXEL_FORMATS);
  imageWidth = models.IntegerField('Image Width (pixels)');
  imageHeight = models.IntegerField('Image Height (pixels)');
  numberColorBands = models.IntegerField('Number of Color Bands');
  imageURL = models.CharField(max_length=1024, unique=True);
  
  #@classmethod
  #Forces everything that is needed to be defined???
  #def create(self, name, fileFormat, pixelFormat, imageWidth, imageHeight, numberColorBands, imgURL):
  #  return Image(name=name, fileFormat=fileFormat, pixelFormat=pixelFormat,
  #               imageWidth=imageWidth, imageHeight=imageHeight, 
  #               numberColorBands=numberColorBands, imgURL=imgURL)

  def __unicode__(self):
    return self.name

class ImageTiePoint(models.Model):
    name = models.CharField(max_length=50)
    #description = models.CharField(max_length=250)
    x = models.FloatField()
    y = models.FloatField()

    userCorrected = models.IntegerField('User Correction', default=0);
    
    image = models.ForeignKey('Image', blank=False)
    geoPoint = models.ForeignKey('GeoTiePoint', null=True, blank=True)

    # Returns the string representation of the model. Documentation says I 
    #need to do this. __unicode__ on Python 2
    def __unicode__(self):
        return self.name

class GeoTiePoint(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()
    
    apparentLatitude = models.FloatField()
    apparentLongitude = models.FloatField()
    apparentAltitude = models.FloatField()
    
    # Returns the string representation of the model. Documentation says I 
    #need to do this. __unicode__ on Python 2
    def __unicode__(self):
        return self.name
