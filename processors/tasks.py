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

def getKTL(image, history=None):
  ''' returns K, T, llh (lon, lat, h)'''
  debug= 0;
  
  camera = image.camera.history(history);
  if debug:
    print "Camera"
    print repr(camera);
  K_i = numpy.eye(3);
  K_i[0,2] = camera.principlePointU;
  K_i[1,2] = camera.principlePointV;
  K_i[0,0] = camera.focalLengthU;
  K_i[1,1] = camera.focalLengthV;
  
  llh = [None];
  
  coordinate_systems = [camera.coordinateSystem.history(history)]
  if debug:
    print "CS1"
    print repr(coordinate_systems)  
  coordinate_transforms = [];
  while len(coordinate_systems[0].coordinatetransform_to_set.all()):
    ct = coordinate_systems[0].coordinatetransform_to_set.all()[0].history(history);
    if debug:
      print "CT"
      print repr(ct)
    #cs = ct.coordinateSystem_from.get_subclasses()[0];
    cs = ct.coordinateSystem_from.history(history);
    if debug:
      print "CS"
      print repr(cs)
    coordinate_transforms = [ct]+coordinate_transforms;
    coordinate_systems = [cs] + coordinate_systems;
  
  if isinstance(coordinate_systems[0], meta.models.GeoreferenceCoordinateSystem):
    llh = list(coordinate_systems[0].history(history).location);
    if debug:
      print "llh"
      print llh
  
  T_camera_0 = numpy.eye(4);
  for ct in coordinate_transforms:
    T = numpy.eye(4);
    T[0,0:3] = ct.rodriguezX;
    T[1,0:3] = ct.rodriguezY;
    T[2,0:3] = ct.rodriguezZ;
    T[0:3, 3] = ct.translation;
    T_camera_0 = T.dot(T_camera_0);
    
  if debug:
    print 'Final T'
    print T_camera_0
    
  return (K_i, T_camera_0, llh);

def projectPoint(K, T, llh_xyz, xs, ys, distances=None, zs=None):
  ''' Project a set of points xs, ys (Nx1 numpy array each) through the K (3x3) T (4x4) 
      model at llh_xyz (3x1). You must either specify the distances to project
      (scalar) or the z intersection planes (scalar)
      
      returns dictionary with lon, lat, h'''
  import enu;
  
  debug = 0;
  
  if debug:
    print 'xyz', xs,ys,zs

  R = T[0:3, 0:3];
  t = T[0:3, 3:]; #Extract 3x1, which is why the : is necessary
  cam_center = -R.T.dot(t);
  if debug:
    print 'Cam_center', cam_center
  P = K.dot(numpy.concatenate((R,t), axis=1));
  Pi = numpy.matrix(P).I;
  if debug:
    print 'P'
    print repr(P)
    print numpy.linalg.pinv(P)
    print 'Pi', Pi
    print [xs,ys,numpy.ones(xs.shape)]
  ray = numpy.array(Pi).dot([xs,ys,numpy.ones(xs.shape)]);
  if debug:
    print 'ray is currently', ray
  


  if abs(ray[3,0]) < 1e-6:
    ray = cam_center + ray[0:3,0:]
  else:
    ray = ray[0:,:]/ray[3,:]; #dehomoginize
  
  if debug:
    print llh_xyz
    print 'ray was', ray
  
  #dp = (P[2:3,:].T * ray[:]).sum(axis=0);
  # Principle plane dot ray
  # NOT WORKING
  #if ray[3] < 0:
  #  dp *= -1;
  #print 'dot',dp 

  ray = cam_center-ray[0:3,:]


  for c in range(ray.shape[1]):
    if distances is None:
      t = (zs - llh_xyz[2] - cam_center[2])/ray[2,c]; #project to sea level
    else:
      t = -distances / numpy.linalg.norm(ray[:,c]);
      #WHY is that minus sign there? Tried the dot product test above, didn't help
    if debug:
      print 't', t
      print 'cam_center', cam_center
    ray[:,c:c+1] = ray[:,c:c+1] * t + cam_center;
  if debug:
    print 'ray is now', ray 

  llh2_xyz = enu.enu2llh(lon_origin=llh_xyz[0], lat_origin=llh_xyz[1], h_origin=llh_xyz[2], east=ray[0,:], north=ray[1,:], up=ray[2,:])
  return llh2_xyz

class NumpyAwareJSONEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, numpy.ndarray) and obj.ndim == 1:
      return obj.tolist()
    return json.JSONEncoder.default(self, obj)

@app.task
def fetchCameraFrustum(**kwargs):
  try:
    imageId = int(kwargs["imageId"])
    image = meta.models.Image.objects.get(id=imageId)
    size = int(kwargs.pop('size', 100)); #Size in meters
    historyId = kwargs.pop('history', None)
    output = kwargs.pop('output', 'json')
    
    if historyId:
      historyId = int(historyId);
    history = meta.models.History.to_dict(historyId)
    if image.camera:
      w = image.imageWidth;
      h = image.imageHeight;
      K, T, llh = getKTL(image, history);
      llh1 = projectPoint(K, T, llh, numpy.array([0]), numpy.array([0]), distances=0) 
      llh2 = projectPoint(K, T, llh, numpy.array([0,w,w,0]), numpy.array([0,0,h,h]), distances=size)
  
      llh2['lon'] = numpy.concatenate((llh1['lon'], llh2['lon']))
      llh2['lat'] = numpy.concatenate((llh1['lat'], llh2['lat']))
      llh2['h']   = numpy.concatenate((llh1['h'],   llh2['h']))
      
      if output == 'json':
        return json.dumps(llh2, cls=NumpyAwareJSONEncoder);
      elif output == 'kml':
        kml = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
  <name>KmlFile</name>
  <Style id="s_ylw-pushpin">
    <IconStyle>
      <scale>1.1</scale>
      <Icon>
        <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
      </Icon>
      <hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
    </IconStyle>
  </Style>
  <StyleMap id="m_ylw-pushpin">
    <Pair>
      <key>normal</key>
      <styleUrl>#s_ylw-pushpin</styleUrl>
    </Pair>
    <Pair>
      <key>highlight</key>
      <styleUrl>#s_ylw-pushpin_hl</styleUrl>
    </Pair>
  </StyleMap>
  <Style id="s_ylw-pushpin_hl">
    <IconStyle>
      <scale>1.3</scale>
      <Icon>
        <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
      </Icon>
      <hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
    </IconStyle>
  </Style>
  <Placemark>
    <name>Untitled Path</name>
    <styleUrl>#m_ylw-pushpin</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <altitudeMode>absolute</altitudeMode>
      <coordinates>'''
        for x in [0,1,0,2,0,3,0,4,3,2,1,4]:
          kml += '%0.12g,%0.12g,%0.12g ' % (llh2['lon'][x], llh2['lat'][x], llh2['h'][x]);
        kml += '''      </coordinates>
    </LineString>
  </Placemark>
</Document>
</kml>'''
        return kml;
  except meta.models.Image.DoesNotExist:
    pass;
  
  return '';
  
  
@app.task
def fetchCameraRay(**kwargs):
  import enu;

  try:
    imageId = int(kwargs["imageId"])
    image = meta.models.Image.objects.get(id=imageId)
    x = int(kwargs.pop('X', image.imageWidth/2))
    y = int(kwargs.pop('Y', image.imageHeight/2))
    height = int(kwargs.pop('height', 0))
    historyId = kwargs.pop('history', None)
    if historyId:
      historyId = int(historyId);
    history = meta.models.History.to_dict(historyId)
  
    if image.camera:
      K, T, llh = getKTL(image, history);
      llh1 = projectPoint(K, T, llh, numpy.array([x]), numpy.array([y]), distances=0) 
      llh2 = projectPoint(K, T, llh, numpy.array([x]), numpy.array([y]), zs=numpy.array([height]))

      llh2['lon'] = numpy.concatenate((llh1['lon'], llh2['lon']))
      llh2['lat'] = numpy.concatenate((llh1['lat'], llh2['lat']))
      llh2['h']   = numpy.concatenate((llh1['h'], llh2['h']))

      return json.dumps(llh2, cls=NumpyAwareJSONEncoder);
  except meta.models.Image.DoesNotExist:
    pass

  return '';

@app.task(base=VipTask, bind=True)
def add_arducopter_images(self, *args, **kwargs):
  images = glob(path_join(os.path.join(env['VIP_PROJECT_ROOT'], 'images'), '1fps*', ''));
  images.sort();
  imageCollection = [];
  for image in images:
    image = os.path.basename(os.path.dirname(image));
    frameNum = image[11:15]
    if meta.models.Image.objects.filter(name="Arducopter Mission 2 Frame:%s" % frameNum):
      raise Exception('Already exists');
    img = meta.models.Image.create(name="Arducopter Mission 2 Frame:%s" % frameNum, imageWidth=4096, imageHeight=2160, 
                             numberColorBands=3, pixelFormat='b', fileFormat='zoom', 
                             imageURL='http://%s/%s/%s/' % (env['VIP_IMAGE_SERVER_AUTHORITY'], env['VIP_IMAGE_SERVER_URL_PATH'], image),
                             service_id = self.request.id);
    img.save();
    
    imageCollection.append(img.id);
    
  ic = meta.models.ImageCollection.create(name="Arducopter Mission 2", service_id = self.request.id);
  ic.save();
  ic.images.add(*imageCollection);
  
  with open(path_join(os.environ['VIP_DATABASE_DIR'], 'Contractor_Survey_NorthA_List.csv'), 'r') as fid:
    lines = fid.readlines();
  lines = map(lambda x: x.split(','), lines);
  
  for line in lines[3:]:
    name = line[1];
    desc = line[2];
    lat = float(line[3]) + float(line[4])/60.0 + float(line[5])/3600.0;
    if line[6] == 'S':
      lat = -lat;
    lon = float(line[8]) + float(line[9])/60.0 + float(line[10])/3600.0;
    if line[11] == 'W':
      lon = -lon;
    alt = float(line[13]);
    
    point = geos.Point(lon, lat, alt)
      
    tp = meta.models.ControlPoint.create(name=name,
                                         description=desc,
                                         point=point,
                                         apparentPoint=point)
    tp.service_id = self.request.id;
    tp.save();

@app.task(base=VipTask, bind=True)
def add_sample_images(self, imageDir, *args, **kwargs):
  ''' Demo ware only really '''
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
  add_sample_cameras(self, path_join(os.environ['VIP_DATABASE_DIR'], 'purdue_cameras_1.txt')) #history = 1
  add_sample_cameras(self, path_join(os.environ['VIP_DATABASE_DIR'], 'purdue_cameras_2.txt')) #history = 2
  add_sample_cameras(self, path_join(os.environ['VIP_DATABASE_DIR'], 'purdue_cameras_3.txt')) #history = 3
  add_sample_cameras(self, path_join(os.environ['VIP_DATABASE_DIR'], 'purdue_cameras_4.txt')) #history = 4
  
def add_sample_cameras(self, filename):

  with open(filename, 'r') as fid:
    history = dict();
    #create a history object for the entire file for the demo
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
        
      history[grcs.objectId] = grcs.id;

      last_cs = grcs;
      for t in range(len(ts)):
# This logic just doesn't work with the cheap getKTL and history tricks currently implemented, NEEDS TO BE REDONE
# Basically reverse FK'd don't work well with history... YET
# My JSON trick SHOULD work.... Maybe
#        try:
#          cs = meta.models.CartesianCoordinateSystem.objects.get(name='%s %d' % (base_filename, t+1), newerVersion=None)
#        except meta.models.CartesianCoordinateSystem.DoesNotExist:
        try:
          cs = meta.models.CartesianCoordinateSystem.objects.get(name='%s %d' % (base_filename, t+1), newerVersion=None)
          cs.service_id = self.request.id;
          cs.update();
        except:
          cs = meta.models.CartesianCoordinateSystem.create(name='%s %d' % (base_filename, t+1),
                                                    service_id = self.request.id,
                                                    xUnit='m', yUnit='m', zUnit='m');
          cs.save();
          
        history[cs.objectId] = cs.id;

        rx = geos.Point(*ts[t][0][0:3]);
        ry = geos.Point(*ts[t][1][0:3]);
        rz = geos.Point(*ts[t][2][0:3]);
        translation = geos.Point(ts[t][0][3], ts[t][1][3], ts[t][2][3]);

        try:
          transform = meta.models.CartesianTransform.objects.get(name='%s %d_%d' % (base_filename, t+1, t), newerVersion=None)
          transform.service_id = self.request.id;
          transform.coordinateSystem_from_id=last_cs.id;
          transform.coordinateSystem_to_id=cs.id;
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
          
        history[transform.objectId] = transform.id;
        last_cs = cs;

      try:
        camera = meta.models.Camera.objects.get(name=base_filename, newerVersion=None);
        camera.service_id = self.request.id;
        camera.update(focalLengthU=k_i[0], focalLengthV=k_i[1],
                      principlePointU=k_i[2], principlePointV=k_i[3],
                      coordinateSystem=last_cs)
      except meta.models.Camera.DoesNotExist:
        camera = meta.models.Camera.create(name=base_filename,
                                         service_id = self.request.id,
                                         focalLengthU=k_i[0],
                                         focalLengthV=k_i[1],
                                         principlePointU=k_i[2],
                                         principlePointV=k_i[3],
                                         coordinateSystem=last_cs)
        camera.save();
        
      history[camera.objectId] = camera.id;
        
        
      #No longer necessary with the Django inspired "Leave the FK alone" technique

      images = meta.models.Image.objects.filter(imageURL__contains=base_filename);

      for img in images:
        #img.service_id = self.request.id;
        img.camera_id = camera.id;
        #img.update();
        img.save()
        
        history[img.objectId] = img.id;
        
  history = meta.models.History(name=filename, history=json.dumps(history))
  history.save();

@app.task(base=VipTask, bind=True)
def add_control_point(self, controlpoint_filename):
  from math import copysign
  with open(controlpoint_filename, 'r') as fid:
    lines = fid.readlines();
  lines = map(lambda x: x.split(','), lines)
  for line in lines:
    name = line[0];
    #Get just the name, the only text field
    fields = map(float, line[1:])
    #Float cast the rest
    
    latitude  = fields[0]
    latitude += copysign(fields[1]/60.0 + fields[2]/3600.0, latitude);
    longitude = fields[3]
    longitude += copysign(fields[4]/60.0 + fields[5]/3600.0, longitude);
    altitude  = fields[6]
    point = 'SRID=4326;POINT(%0.12f %0.12f %0.12f)' % (longitude, latitude, altitude);

    other = 'Utm %f %f %f Other %f %f %f' % tuple(fields[7:])
    tp = meta.models.ControlPoint.create(name=name,
                                         description=other,
                                         point=point,
                                         apparentPoint=point)
    tp.service_id = self.request.id;
    tp.save();

@app.task(base=VipTask, bind=True)
def add_sample_tie_point(self, site_filename, lvcs_selected_filename, camera, frames):
  ''' Demo ware only, really '''
  from tools.xml_dict import load_xml
  control_point_names = [];
  with open(lvcs_selected_filename, 'r') as fid:
    for line in fid:
      control_point_names.append(line.split(' ')[0])
  tie_point_data = load_xml(site_filename);
  
  for control_point_index in range(len(control_point_names)):
    cpn = control_point_names[control_point_index];
    cp = meta.models.ControlPoint.objects.get(name=cpn);
    for frame in frames:
      tp = tie_point_data['Correspondences']['Correspondence'][control_point_index]['CE'].find_at(fr__is='%d'%frame);
      if tp:
        tp = tp[0].at;
        name = '%s Camera:%d Frame:%03d' % (cpn, camera, int(frame))
        point = 'POINT(%s %s)' % (tp['u'], tp['v']);
        image = meta.models.Image.objects.get(name__contains='Camera:%d Frame:%03d' % (camera, frame))
        tp = meta.models.TiePoint.create(name=name, point=point, image=image, geoPoint=cp)
        tp.service_id = self.request.id;
        tp.save();
        
@app.task(base=VipTask, bind=True)
def update_sample_tie_point(self, tiepoint_filename):
  ''' Demo ware only, really '''
  with open(tiepoint_filename, 'r') as fid:
    lines = fid.readlines();
  lines = map(lambda x: x.split('\x00'), lines)
  
  for tp in lines:
    img = meta.models.Image.objects.get(name=tp[0], newerVersion=None)
    cp = meta.models.ControlPoint.objects.get(name=tp[1], newerVersion=None)
    TP = meta.models.TiePoint.objects.get(geoPoint=cp, image=img, newerVersion=None)
    
    TP.service_id = self.request.id;
    TP.point = 'POINT(%s %s)' % (tp[2], tp[3].strip())
    TP.update()
  

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
