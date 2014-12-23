
import logging
logger = logging.getLogger();
import voxel_globe.meta.models as models
from django.contrib.gis.geos import Point

def saveKrt(service_id, image, k, r, t, origin, srid=4326):
  '''Saves the appropriate krt model to the image
  
     Keyword Arguments:
     service_id - Id field from the celery task calling this function
     image - voxel_globe.meta.Image object or object_id number
     k - 3x3 numpy.array
     r - 3x3 numpy.array
     t - 3 numpy.array
     origin - 3 numpy.arry, longitude, latitude, altitude in xyz order
     srid - srid number for origin
  '''

  if not hasattr(image, 'name'): #duck type, for maximum flexibility
    image =  models.Image.objects.get(id=image)

#  (k,r,t) = cam.krt(width=image.imageWidth, height=image.imageHeight);
  logger.info('Origin is %s' % str(origin))

  grcs = models.GeoreferenceCoordinateSystem.create(
                  name='%s 0' % image.name,
                  xUnit='d', yUnit='d', zUnit='m',
                  location='SRID=%d;POINT(%0.15f %0.15f %0.15f)' 
                            % (srid, origin[0], origin[1], origin[2]),
                  service_id = service_id)
  grcs.save()
  cs = models.CartesianCoordinateSystem.create(
                  name='%s 1' % (image.name),
                  service_id = service_id,
                  xUnit='m', yUnit='m', zUnit='m');
  cs.save()

  transform = models.CartesianTransform.create(
                       name='%s 1_0' % (image.name),
                       service_id = service_id,
                       rodriguezX=Point(*r[0,:]),
                       rodriguezY=Point(*r[1,:]),
                       rodriguezZ=Point(*r[2,:]),
                       translation=Point(t[0], t[1], t[2]),
                       coordinateSystem_from_id=grcs.id,
                       coordinateSystem_to_id=cs.id)
  transform.save()

  camera = image.camera;
  try:
    camera.update(service_id = service_id,
                  focalLengthU=k[0,0],   focalLengthV=k[1,1],
                  principalPointU=k[0,2], principalPointV=k[1,2],
                  coordinateSystem=cs);
  except:
    camera = models.Camera.create(name=image.name,
                  service_id = service_id,
                  focalLengthU=k[0,0],   focalLengthV=k[1,1],
                  principalPointU=k[0,2], principalPointV=k[1,2],
                  coordinateSystem=cs);
    camera.save();
    image.update(camera = camera);
