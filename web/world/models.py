from django.contrib.gis.db import models

class WorldBorder(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.IntegerField('Population 2005')
    fips = models.CharField('FIPS Code', max_length=2)
    iso2 = models.CharField('2 Digit ISO', max_length=2)
    iso3 = models.CharField('3 Digit ISO', max_length=3)
    un = models.IntegerField('United Nations Code')
    region = models.IntegerField('Region Code')
    subregion = models.IntegerField('Sub-Region Code')
    lon = models.FloatField()
    lat = models.FloatField()

    # GeoDjango-specific: a geometry field (MultiPolygonField), and
    # overriding the default manager with a GeoManager instance.
    mpoly = models.MultiPolygonField()
    objects = models.GeoManager()

    # Returns the string representation of the model.
    def __unicode__(self):              # __unicode__ on Python 2
        return self.name

    def closeToUS(self):
      return abs(self.lon+98.606)+abs(self.lat-39.622)<50

class TestTable(models.Model):
  name = models.CharField(max_length=50)
  bookId = models.IntegerField()

  def __unicode__(self):
    return self.name;

  def __repr__(self):
    return 'Book:\t%s\nId:\t%s\n' % (self.name, self.bookId)

class Favorites(models.Model):
  name = models.CharField(max_length=200);
  favoriteBook = models.ForeignKey(TestTable)

  def __unicode__(self):
    return self.name

  def __repr__(self):
    return 'Name:\t%s\nFavorite Books:\t%s\n' % (self.name, self.favoriteBook)

