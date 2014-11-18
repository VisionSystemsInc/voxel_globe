import numpy

def getKTO(image, history=None):
  ''' returns K, T, llh_origin (lon, lat, h)'''
  import voxel_globe.meta.models
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
