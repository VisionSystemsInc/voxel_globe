from ..common_tasks import app, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

@app.task(base=VipTask, bind=True)
def runVisualSfm(self, imageCollectionId, sceneId, history=None):
  from voxel_globe.meta import models
  from ..order.visualsfm.models import Order
  from tempfile import mkdtemp;

  from os import environ as env
  from os.path import join as path_join
  import os
  
  from .tools import writeNvm, writeGcpFile, generateMatchPoints, runSparse, readNvm
  
  from voxel_globe.tools.wget import download as wget
  from ..meta.tools import getKTO
  import voxel_globe.tools.enu as enu
  import numpy
  
  from django.contrib.gis.geos import Point

  self.update_state(state='INITIALIZE', meta={'stage':0})

  #Make main temp dir
  if not os.path.exists(env['VIP_TEMP_DIR']):
    from distutils.dir_util import mkpath
    mkpath(env['VIP_TEMP_DIR']);
  #make instance specific directory
  if env['VIP_CONSTANT_TEMP_DIR'] == '1':
    processingDir = env['VIP_TEMP_DIR'];
  else:
    processingDir = mkdtemp(dir=env['VIP_TEMP_DIR']);
  matchFilename = path_join(processingDir, 'match.nvm');
  sparceFilename = path_join(processingDir, 'sparse.nvm');
  gcpFilename = matchFilename + '.gcp' #This can NOT be changed in version 0.5.25  
  logger.debug('Task %s is processing in %s' % (self.request.id, processingDir))

  imageCollection = models.ImageCollection.objects.get(id=imageCollectionId).history(history);
  imageList = imageCollection.images.all();
  
  #A Little bit of database logging
  oid = Order(processingDir=processingDir, imageCollection=imageCollection)
  

  localImageList = [];
  for x in range(len(imageList)):
    #Download the image locally
    self.update_state(state='INITIALIZE', meta={'stage':'image fetch', 'i':x, 'total':len(imageList)})
    imageName = imageList[x].originalImageUrl;
    extension = os.path.splitext(imageName)[1]
    localName = path_join(processingDir, 'frame_%05d%s' % (x+1, extension)); 
    wget(imageName, localName, secret=True)

    #Convert the image if necessary    
    if extension not in ['.jpg', '.pgm', '.ppm']:
      self.update_state(state='INITIALIZE', meta={'stage':'image convert', 'i':x, 'total':len(imageList)})
      #Add code here to converty to jpg for visual sfm
      if extension=='not implemented':
        newLocalName = os.path.splitext(localName)[0] + '.jpg';
        #stuff, maybe call gdal?
        localName = newLocalName;
      else:
        raise Exception('Unsupported file type');
      
    imageInfo = {'localName':localName, 'index':x}

    try:
      [K, T, llh] = getKTO(imageList[x], history=history);
      imageInfo['K_intrinsics'] = K;
      imageInfo['transformation'] = T;
      imageInfo['enu_origin'] = llh;
    except:
      pass

    localImageList.append(imageInfo);
  
#  filenames = list(imageList.values_list('imageUrl'))
#  logger.info('The image list 0is %s' % filenames)

  self.update_state(state='PROCESSING', meta={'stage':'generate match points', 
                                              'processingDir':processingDir,
                                              'total':len(imageList)})
  generateMatchPoints(map(lambda x:x['localName'], localImageList),
                      matchFilename, logger=logger)
  
  self.update_state(state='PROCESSING', meta={'stage':'writing gcp points'})
#   cameras = [];
#   for image in imageList:
#     if 1:
#     #try:
#       [K, T, llh] = getKTO(image);
#       cameras.append({'image':image.id, 'K':K, 'tranformation':T, 'origin':llh})
#     #except:
#       pass  

#  origin = numpy.median(origin, axis=0)
#  origin = [-92.215197, 37.648858, 268.599]
  origin = list(models.Scene.objects.get(id=sceneId).origin) 
  #find the middle origin, and make it THE origin
  data = []#.name .llh_xyz
  for imageInfo in localImageList:
    try:
      r = imageInfo['transformation'][0:3, 0:3]
      t = imageInfo['transformation'][0:3, 3:]
      enu_point = -r.transpose().dot(t);

      if not numpy.array_equal(imageInfo['enu_origin'], origin):
        ecef = enu.enu2xyz(refLong=imageInfo['enu_origin'][0],
                           refLat=imageInfo['enu_origin'][1],
                           refH=imageInfo['enu_origin'][2],
                           #e=imageInfo['transformation'][0, 3],
                           #n=imageInfo['transformation'][1, 3],
                           #u=imageInfo['transformation'][2, 3])
                           e=enu_point[0],
                           n=enu_point[1],
                           u=enu_point[2])
        enu_point = enu.xyz2enu(refLong=origin[0], 
                                refLat=origin[1], 
                                refH=origin[2],
                                X=ecef[0],
                                Y=ecef[1],
                                Z=ecef[2])
#      else:
#        enu_point = imageInfo['transformation'][0:3, 3];
      
      dataBit = {'filename':imageInfo['localName'], 'xyz':enu_point}
      data.append(dataBit);
    except: #some images may have no camera 
      pass
  oid.lvcsOrigin = str(origin)
  oid.save()

  #Make this a separate injest process, making CAMERAS linked to the images
  #data = arducopter.loadAdjTaggedMetadata(r'd:\visualsfm\arducopter\2014-03-20 13-22-44_adj_tagged_images.txt');
  #Make this read the cameras from the DB instead
  writeGcpFile(data, gcpFilename)

  #runSparse(r'd:\visualsfm\arducopter\match.nvm', r'd:\visualsfm\arducopter\sparse.nvm', gcp=True, shared=True)
  self.update_state(state='PROCESSING', meta={'stage':'sparse SFM'})
  runSparse(matchFilename, sparceFilename, gcp=True, shared=True, logger=logger)

  self.update_state(state='FINALIZE', meta={'stage':'loading resulting cameras'})
  
  
  cams = readNvm(path_join(processingDir, 'sparse.nvm'))
  #cams.sort(key=lambda x:x.name)
  #Since the file names are frame_00001, etc... You KNOW this order is identical to 
  #localImageList, with some missing
  for cam in cams:
    frameName = cam.name; #frame_00001, etc....
    imageInfo = filter(lambda x: x['localName'].endswith(frameName), localImageList)[0]
    #I have to use endswith instead of == because visual sfm APPARENTLY 
    #decides to take some libery and make absolute paths relative
    image = imageList[imageInfo['index']]

    (k,r,t) = cam.krt(width=image.imageWidth, height=image.imageHeight);
    logger.info('Origin is %s' % str(origin))
    llh_xyz = enu.enu2llh(lon_origin=origin[0], 
                          lat_origin=origin[1], 
                          h_origin=origin[2], 
                          east=cam.translation_xyz[0], 
                          north=cam.translation_xyz[1], 
                          up=cam.translation_xyz[2])
        
    grcs = models.GeoreferenceCoordinateSystem.create(
                    name='%s 0' % image.name,
                    xUnit='d', yUnit='d', zUnit='m',
                    location='SRID=4326;POINT(%0.15f %0.15f %0.15f)' 
#                              % (llh_xyz['lon'], llh_xyz['lat'], llh_xyz['h']),
                              % (origin[0], origin[1], origin[2]),
                    service_id = self.request.id)
    grcs.save()
    cs = models.CartesianCoordinateSystem.create(
                    name='%s 1' % (image.name),
                    service_id = self.request.id,
                    xUnit='m', yUnit='m', zUnit='m');
    cs.save()

    transform = models.CartesianTransform.create(
                         name='%s 1_0' % (image.name),
                         service_id = self.request.id,
                         rodriguezX=Point(*r[0,:]),
                         rodriguezY=Point(*r[1,:]),
                         rodriguezZ=Point(*r[2,:]),
                         translation=Point(t[0][0], t[1][0], t[2][0]),
                         coordinateSystem_from_id=grcs.id,
                         coordinateSystem_to_id=cs.id)
    transform.save()
    
    camera = image.camera;
    try:
      camera.update(service_id = self.request.id,
                    focalLengthU=k[0,0],   focalLengthV=k[1,1],
                    principalPointU=k[0,2], principalPointV=k[1,2],
                    coordinateSystem=cs);
    except:
      camera = models.Camera.create(name=image.name,
                    service_id = self.request.id,
                    focalLengthU=k[0,0],   focalLengthV=k[1,1],
                    principalPointU=k[0,2], principalPointV=k[1,2],
                    coordinateSystem=cs);
      camera.save();
      image.update(camera = camera);
  
  logger.info(str(cams[0]))

  return oid.id;