import numpy
import voxel_globe.meta.models
import inspect

def _getHistory(histories):
  ''' Returns dictionary for specific service ids. This has no real use.
      You should probably be using getHistory that uses this function '''
  
  matches = []
  for model in inspect.getmembers(voxel_globe.meta.models, inspect.isclass):
    if issubclass(model[1], voxel_globe.meta.models.VipObjectModel) and model[1] is not voxel_globe.meta.models.VipObjectModel:
      matches.extend(model[1].objects.filter(service_id__in=histories).values_list('id', 'objectId', 'service_id')) 
  
  d = {}
  for history in histories:
    tmp = filter(lambda x:x[2]==history, matches)
    try:
      id, objectId, tmp = zip(*tmp)
      d.update(dict(zip(objectId, id)))
    except ValueError:
      pass;
  
  return d

def getHistory(history=None, include=True):
  ''' Helper function to create a snapshot in history either just before or
      after a specific service. Can be specifies by DMO object or id
      include=True - Include this service ID's history (after)
      include=False - Do not include this service ID's history (before)
      
      Note: This will probably get expensive as the database grows''' 
  
  if history is None:
    return {};
  
  if not isinstance(history, voxel_globe.meta.models.ServiceInstance):
    history = voxel_globe.meta.models.ServiceInstance.objects.get(id=history)

  histories = list(voxel_globe.meta.models.ServiceInstance.objects.filter(finishTime__lt=history.finishTime).order_by('finishTime').values_list('id', flat=True))
  if include:
    histories.append(history.id);

  return _getHistory(histories)

def getKto(image, history=None):
  ''' returns K, T, llh_origin (lon, lat, h)'''
  debug= 0;
  
  camera = image.camera.history(history);
  if debug:
    print "Camera"
    print repr(camera);
  K_i = numpy.eye(3);
  K_i[0,2] = camera.principalPointU;
  K_i[1,2] = camera.principalPointV;
  K_i[0,0] = camera.focalLengthU;
  K_i[1,1] = camera.focalLengthV;
  
  llh = [None];
  
  coordinate_systems = [camera.coordinateSystem.history(history)]
  if debug:
    print "CS1"
    print repr(coordinate_systems)  
  coordinate_transforms = [];
  while len(coordinate_systems[0].coordinatetransform_to_set.all()):
    #While the first coordinate system has a transform, pre-pend it to the list
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
  
  if isinstance(coordinate_systems[0], voxel_globe.meta.models.GeoreferenceCoordinateSystem):
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

def getKrt(image, origin=None, history=None, eps=1e-9):
  ''' returns K, T, llh_origin (lon, lat, h)'''
  camera = image.camera.history(history);
  K_i = numpy.eye(3);
  K_i[0,2] = camera.principalPointU;
  K_i[1,2] = camera.principalPointV;
  K_i[0,0] = camera.focalLengthU;
  K_i[1,1] = camera.focalLengthV;
  
  llh = [None];
  
  coordinate_systems = [camera.coordinateSystem.history(history)]
  coordinate_transforms = [];
  while len(coordinate_systems[0].coordinatetransform_to_set.all()):
    #While the first coordinate system has a transform, pre-pend it to the list
    ct = coordinate_systems[0].coordinatetransform_to_set.all()[0].history(history);

    #cs = ct.coordinateSystem_from.get_subclasses()[0];
    cs = ct.coordinateSystem_from.history(history);
    coordinate_transforms = [ct]+coordinate_transforms;
    coordinate_systems = [cs] + coordinate_systems;
  
  if isinstance(coordinate_systems[0], voxel_globe.meta.models.GeoreferenceCoordinateSystem):
    llh = list(coordinate_systems[0].history(history).location);
  
  T_camera_0 = numpy.eye(4);
  for ct in coordinate_transforms:
    T = numpy.eye(4);
    T[0,0:3] = ct.rodriguezX;
    T[1,0:3] = ct.rodriguezY;
    T[2,0:3] = ct.rodriguezZ;
    T[0:3, 3] = ct.translation;
    T_camera_0 = T.dot(T_camera_0);
    
    R = T_camera_0[0:3, 0:3];
    t = T_camera_0[0:3, 3:4];
    
  if origin:
    if numpy.abs(numpy.array(llh)-origin).max() > eps:
      pass#Convert to different origin. WARNING, less stable
  return (K_i, R, t, llh);

def getLlh(image, history=None):
  import voxel_globe.tools.enu as enu

  (k,r,t,origin)= getKrt(image, history=history)
  cameraCenter = -r.T.dot(t)
  
  llh =  enu.enu2llh(lon_origin=origin[0], 
                     lat_origin=origin[1], 
                     h_origin=origin[2], 
                     east=cameraCenter[0], 
                     north=cameraCenter[1], 
                     up=cameraCenter[2])
  
  return (llh['lon'][0], llh['lat'][0], llh['h'][0])

def projectPoint(K, T, llh_xyz, xs, ys, distances=None, zs=None):
  ''' Project a set of points xs, ys (Nx1 numpy array each) through the K (3x3) T (4x4) 
      model at llh_xyz (3x1). You must either specify the distances to project
      (scalar) or the z intersection planes (scalar)
      
      returns dictionary with lon, lat, h'''
  import voxel_globe.tools.enu as enu;
  
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
  # Principal plane dot ray
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

  llh2_xyz = enu.enu2llh(lon_origin=llh_xyz[0], 
                         lat_origin=llh_xyz[1], 
                         h_origin=llh_xyz[2], 
                         east=ray[0,:], 
                         north=ray[1,:], 
                         up=ray[2,:])
  return llh2_xyz
