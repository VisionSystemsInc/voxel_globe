from celery import Celery, Task, group

import scipy;
import numpy;

import world.models
import meta.models
from glob import glob;
from os import environ as env;
from os.path import join as path_join;
import os;

from django.contrib.gis import geos

app = Celery('tasks');
app.config_from_object('celeryconfig') #Don't need this because celeryd does it for me

import json;

@app.task(bind=True)
def add(self, x, y):
  a = numpy.random.random((x,x));
  aaa = a;
  for yy in xrange(y):
    aa = scipy.fft(aaa);
    aaa = scipy.ifft(aa);

  return [numpy.abs(a-aaa).sum(), self.request.id]

@app.task
def getArea(id):
  country = world.models.WorldBorder.objects.get(id=id)
  return country.area;

class VipTask(Task):
  abstract = True
  
  def __createServiceIntanceEntry(self, inputs=None, user="NAY"):
    '''Create initial database entry for service instance, and return the ID'''
    
    serviceInstance = meta.models.ServiceInstance(
                          inputs=json.dumps(inputs),
                          status="Creating",
                          user=user,
                          serviceName=self.name, #Next TODO
                          outputs='NAY');
    serviceInstance.save();
    return str(serviceInstance.id);
    
  def __updateServiceIntanceEntry(self, output, task_id, status,
                                        args=None, kwargs=None):
    try:
      serviceInstance = meta.models.ServiceInstance.objects.get(id=task_id);
      #serviceInstance = meta.models.ServiceInstance.objects.get_for_id(task_id);
    except meta.models.ServiceInstance.DoesNotExist:
      #Else it's just missing, create it
      status="Impromptu:"+status;
      task_id = self.__createServiceIntanceEntry((args, kwargs));
      serviceInstance = meta.models.ServiceInstance.objects.get(id=task_id);

    serviceInstance.outputs = json.dumps(output)
    serviceInstance.status = status;
    serviceInstance.save();

  def apply_async(self, args=None, kwargs=None, task_id=None, *args2, **kwargs2):
    '''Automatically create task_id's based off of new primary keys in the
       database. Ignores specified task_id. I decided that was best''' 
    taskID = self.__createServiceIntanceEntry((args, kwargs));
    
    return super(VipTask, self).apply_async(args=args, kwargs=kwargs, 
                                            task_id=taskID, *args2, **kwargs2)
  
  def apply(self, args=None, kwargs=None, *args2, **kwargs2):
    '''Automatically create task_id's based off of new primary keys in the
       database. Ignores specified task_id. I decided that was best''' 
    if kwargs:
      kwargs.pop('task_id', None); #Remove task_id incase it is specified.
      #apply is different from apply_async in this manner

    taskID = self.__createServiceIntanceEntry((args, kwargs));

    return super(VipTask, self).apply(args=args, kwargs=kwargs, task_id=taskID,
                                      *args2, **kwargs2)
  
#  def after_return(self, status, retval, task_id, args, kwargs, einfo): #, *args2, **kwargs2
  def on_success(self, retval, task_id, args, kwargs):
    #I can't currently tell if apply or apply_asyn is called, but I don't think I care
    self.__updateServiceIntanceEntry(retval, task_id, 'Success', args, kwargs);
  
  def on_failure(self, exc, task_id, args, kwargs, einfo):
    self.__updateServiceIntanceEntry(str(einfo), task_id, 'Failure',
                                     args, kwargs);
    
#  def on_retry(self, exc, task_id, args, kwargs, einfo):
#    pass

@app.task(base=VipTask)
def test(abc=None, *args, **kwargs):
  if abc==15:
    raise Exception("ouch");
  return 42

@app.task(base=VipTask, bind=True)
def addTiePoint(self, *args, **kwargs):
  tp = meta.models.TiePoint.create(*args, **kwargs);
  tp.service_id = self.request.id;
  tp.save();
  return tp.id;

@app.task(base=VipTask, bind=True)
def updateTiePoint(self, id, xc, y, *args, **kwargs):
  tp = meta.models.TiePoint.objects.get(id=id);
  tp.service_id = self.request.id;
  #for key, val in kwargs.iteritems():
  #  tp.
  tp.point = 'POINT(%s %s)' % (xc,y);
  tp.update();
  return tp.id;

@app.task(base=VipTask, bind=True)
def injestImage(self, *args, **kwargs):
  pass

def getKTL(image, history=0):
  import numpy as np
  camera = image.camera.history(history);
  K_i = np.eye(3);
  K_i[0,2] = camera.principlePointU;
  K_i[1,2] = camera.principlePointV;
  K_i[0,0] = camera.focalLengthU;
  K_i[1,1] = camera.focalLengthV;
  
  llh = [None];
  
  coordinate_systems = [camera.coordinateSystem]
  coordinate_transforms = [];
  while len(coordinate_systems[0].coordinatetransform_to_set.all()):
    ct = coordinate_systems[0].coordinatetransform_to_set.all()[0].history(history);
    cs = ct.coordinateSystem_from.get_subclasses()[0];
    coordinate_transforms = [ct]+coordinate_transforms;
    coordinate_systems = [cs] + coordinate_systems;
  
  if isinstance(coordinate_systems[0], meta.models.GeoreferenceCoordinateSystem):
    llh = list(coordinate_systems[0].history(history).location);
  
  T_camera_0 = np.eye(4);
  for ct in coordinate_transforms:
    T = np.eye(4);
    T[0,0:3] = ct.rodriguezX;
    T[1,0:3] = ct.rodriguezY;
    T[2,0:3] = ct.rodriguezZ;
    T[0:3, 3] = ct.translation;
    T_camera_0 = T.dot(T_camera_0);
    
  return (K_i, T_camera_0, llh);


@app.task
def projectRay(**kwargs):
  import numpy as np;
  import enu;
  imageId = int(kwargs["imageId"])
  image = meta.models.Image.objects.get(id=imageId)
  x = int(kwargs.pop('x', image.imageWidth/2))
  y = int(kwargs.pop('y', image.imageHeight/2))
  height = int(kwargs.pop('height', 0))
  history = int(kwargs.pop('history', 0))

  if image.camera:
#    try:
      K, T, llh = getKTL(image, history);
#       print "K is ", K
#       print "T is ", T
#       print "llh is ", llh
      R = T[0:3, 0:3];
      t = T[0:3, 3]; t.shape=(3,1)
      cam_center = -R.dot(t).flatten();
      P = K.dot(np.concatenate((R,t), axis=1));
      Pi = np.matrix(P).I;
      ray = np.array(Pi).dot([[x],[y],[1]]);
      ray = ray[0:3,0].flatten();
#       print "Ray is ", ray
      t = (-llh[2]+height - cam_center[2])/ray[2]; #project to sea level
#       print 'ray * t is ', ray*t
      ray = ray * t+cam_center;
      llh2 = enu.enu2llh(lon_origin=llh[0], lat_origin=llh[1], h_origin=llh[2], east=ray[0], north=ray[1], up=ray[2])
      llh2 = [llh2['lon'], llh2['lat'], llh2['h']]
#       print "Ray is now ", ray
#       print "t is ", t
#       print "llh2 is ", llh2
#       t = distance/ray[2];
      return json.dumps((llh, llh2));

#    except:
      pass

  return '';


@app.task(base=VipTask, bind=True)
def add_sample_images(self, imageDir, *args, **kwargs):
  images = glob(path_join(imageDir, '2010*', ''));
  images.sort();
  imageCollections = {};
  for image in images:
    cam = int(image[-7:-5])
    date = image[-31:-17];
    other = image[-16:-11]
    frameNum = image[-11:-8]
    image = os.path.basename(os.path.dirname(image));
    img = meta.models.Image.create(name="Purdue Data Date:%s Sequence:%s Camera:%d Frame:%s" % (date, other, cam, frameNum), imageWidth=3248, imageHeight=4872, 
                             numberColorBands=1, pixelFormat='b', fileFormat='zoom', 
                             imageURL='http://%s/%s/%s/' % (env['VIP_IMAGE_SERVER_AUTHORITY'], env['VIP_IMAGE_SERVER_URL_PATH'], image),
                             service_id = self.request.id);
    img.save();
    
    imageCollections[cam] = imageCollections.pop(cam, ())+(img.id,);
    
  for cam in range(6):
    ic = meta.models.ImageCollection.create(name="Purdue Dataset Camera %d" % cam, service_id = self.request.id);
    ic.save();
    ic.images.add(*imageCollections[cam]);
  add_sample_cameras(self, path_join(os.environ['VIP_DATABASE_DIR'], 'purdue_cameras_1.txt'))
  add_sample_cameras(self, path_join(os.environ['VIP_DATABASE_DIR'], 'purdue_cameras_2.txt'))
  
def add_sample_cameras(self, filename):

  with open(filename, 'r') as fid:
    for line in fid:
      l = eval(line);
    
      pos_filename = l[0];
      base_filename = os.path.splitext(os.path.split(pos_filename)[-1])[0]
      
      llh = l[1];
      ts = l[2:-1];
      k_i = l[-1];
      
      try:
        grcs = meta.models.GeoreferenceCoordinateSystem.objects.get(name='%s 0' % base_filename, newerVersion=None);
        grcs.service_id = self.request.id;
        grcs.update(location = 'SRID=4326;POINT(%0.12f %0.12f %0.12f)' % tuple(llh));
      except meta.models.GeoreferenceCoordinateSystem.DoesNotExist:
        grcs = meta.models.GeoreferenceCoordinateSystem.create(name='%s 0' % base_filename,
                                                               xUnit='d', yUnit='d', zUnit='m',
                                                               location='SRID=4326;POINT(%0.12f %0.12f %0.12f)' % tuple(llh),
                                                               service_id = self.request.id)
        grcs.save();

      last_cs = grcs;
      for t in range(len(ts)):
        try:
          cs = meta.models.CartesianCoordinateSystem.objects.get(name='%s %d' % (base_filename, t+1), newerVersion=None)
        except meta.models.CartesianCoordinateSystem.DoesNotExist:
          cs = meta.models.CartesianCoordinateSystem.create(name='%s %d' % (base_filename, t+1),
                                                   service_id = self.request.id,
                                                   xUnit='m', yUnit='m', zUnit='m');
          cs.save();

        rx = geos.Point(*ts[t][0][0:3]);
        ry = geos.Point(*ts[t][1][0:3]);
        rz = geos.Point(*ts[t][2][0:3]);
        translation = geos.Point(ts[t][0][3], ts[t][1][3], ts[t][2][3]);

        try:
          transform = meta.models.CartesianTransform.objects.get(name='%s %d_%d' % (base_filename, t+1, t), newerVersion=None)
          transform.service_id = self.request.id;
          transform.update(rodriguezX=rx,rodriguezY=ry,rodriguezZ=rz,
                           translation=translation);
        except meta.models.CartesianTransform.DoesNotExist:
          transform = meta.models.CartesianTransform.create(name='%s %d_%d' % (base_filename, t+1, t),
                                       service_id = self.request.id,
                                       rodriguezX=rx,rodriguezY=ry,rodriguezZ=rz,
                                       translation=translation,
                                       coordinateSystem_from_id=last_cs.id,
                                       coordinateSystem_to_id=cs.id)
          transform.save()

        last_cs = cs;

      try:
        camera = meta.models.Camera.objects.get(name=base_filename, newerVersion=None);
        camera.service_id = self.request.id;
        camera.update(focalLengthU=k_i[0], focalLengthV=k_i[1],
                      principlePointU=k_i[2], principlePointV=k_i[3])
      except meta.models.Camera.DoesNotExist:
        camera = meta.models.Camera.create(name=base_filename,
                                         service_id = self.request.id,
                                         focalLengthU=k_i[0],
                                         focalLengthV=k_i[1],
                                         principlePointU=k_i[2],
                                         principlePointV=k_i[3],
                                         coordinateSystem=last_cs)
        camera.save();

      images = meta.models.Image.objects.filter(imageURL__contains=base_filename);

      for img in images:
        #img.service_id = self.request.id;
        img.camera_id = camera.id;
        #img.update();
        img.save()
        
      #image.update(service=self.request.id, camera=camera.id);

      #map(lambda x:x.update(service=self.request.id, camera=camera), image);

#      transform = meta.models.CartesianTransform(service_id = self.request.id,
#                                       rodriguezX=geos.Point(0,0,0),
#                                       rodriguezY=geos.Point(0,0,0),
#                                       rodriguezZ=geos.Point(0,0,0),
#                                       translation=geos.Point(0,0,0),
#                                       coordinateSystem_from_id=last_cs.id,
#                                       coordinateSystem_to_id=camera.id)
#      transform.save()

@app.task(base=VipTask, bind=True)
def add_controlPoint(self, controlpoint_filename):
  with fid(controlpoint_filename, 'r') as fid:
    pass;
  
@app.task(base=VipTask, bind=True)
def add_sample_data(self):
  '''Add regression data to database.
  
     This function is primarily used by initialize_database.py to create test
     data for going into the database.'''

  img = meta.models.Image.create(name="Oxford Codrington Library", imageWidth=999, imageHeight=749, 
                                 numberColorBands=3, pixelFormat='b', fileFormat='zoom', 
                                 imageURL='http://%s/%s/camelot-UK_2012OxfordUniversity-42/' % 
                                    (env['VIP_IMAGE_SERVER_AUTHORITY'], env['VIP_IMAGE_SERVER_URL_PATH']));
  img.service_id = self.request.id;
  img.save()

  ic = meta.models.ImageCollection.create(name="Oxford Libraries", service_id = self.request.id);
  ic.save();
  ic.images.add(img);
  #No saving needed for this.

  tp = meta.models.TiePoint.create(point=geos.Point(x=100, y=101), name='Some point', image = img);
  tp.service_id = self.request.id;

  gtp = meta.models.ControlPoint.create(name='Some geo point', 
           description='None provided. Just some point trying to make a point in life',
           point=geos.Point(x=-1.2539, y=51.7534, z=89.2, srid=4326),
           #latitude=51.7534, longitude=-1.2539, altitude=89.2,
           apparentPoint=geos.Point(x=-1.254033, y=51.753416, z=71, srid=4326))
#           apparentLatitude=51.753416, apparentLongitude=-1.254033, apparentAltitude=71)

  gtp.service_id = self.request.id;
  gtp.save();

  tp.geoPoint = gtp;
  tp.save();
  
  return [img.id, tp.id, gtp.id] 

@app.task
def deleteServiceInstance(service_id):
  ''' Maintanence routine '''
  serviceInstance = meta.models.ServiceInstance.objects.get(id=service_id);
  
  sets = filter(lambda x: x.endswith('_set'), dir(serviceInstance))
  
  for s in sets:
    objects = getattr(serviceInstance, s).all();
    for obj in objects:
      #parents = getattr(objects, s).all();
      #It will be called the same thing, I hope... The only way this wouldn't
      #be true is if the model definition was REALLY messed up, which shouldn't
      #Be possible with my inheritance schema. So this should always work
      #for parent in parents:
      print 'Dereferencing %s %s %d' % (type(obj), obj.name, obj.id)
      obj.remove_reference();

  print 'Deleting Service Instance tree'
  serviceInstance.delete();

  
#TODO
#Define Add task
#--Addes a task, retrieve data from database, etc...
#--Gets a GUID and sets task ID
#--Adds entry for service/taskID into ____ table

#Workflows?
#Need to read up on Celery to see if it already does workflows

'''
Avoid launching synchronous subtasks

Having a task wait for the result of another task is really inefficient, and may even cause a deadlock if the worker pool is exhausted.

Make your design asynchronous instead, for example by using callbacks.

Bad:

@app.task
def update_page_info(url):
    page = fetch_page.delay(url).get()
    info = parse_page.delay(url, page).get()
    store_page_info.delay(url, info)

@app.task
def fetch_page(url):
    return myhttplib.get(url)

@app.task
def parse_page(url, page):
    return myparser.parse_document(page)

@app.task
def store_page_info(url, info):
    return PageInfo.objects.create(url, info)

Good:

def update_page_info(url):
    # fetch_page -> parse_page -> store_page
    chain = fetch_page.s() | parse_page.s() | store_page_info.s(url)
    chain()

@app.task()
def fetch_page(url):
    return myhttplib.get(url)

@app.task()
def parse_page(page):
    return myparser.parse_document(page)

@app.task(ignore_result=True)
def store_page_info(info, url):
    PageInfo.objects.create(url=url, info=info)

Here I instead created a chain of tasks by linking together different subtask()'s. You can read about chains and other powerful constructs at Canvas: Designing Workflows.'''
