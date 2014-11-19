from ..common_tasks import app, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

@app.task(base=VipTask, bind=True)
def runVisualSfm(self, imageCollectionId):
  from voxel_globe.meta import models
  from ..order.visualsfm.models import Order
  from tempfile import mkdtemp;

  from os import environ as env
  from os.path import join as path_join
  import os
  
  from .tools import writeNvm, writeGcpFileEnu, generateMatchPoints, runSparse, readNvm
  
  from voxel_globe.tools.wget import download as wget
  from ..meta.tools import getKTO
  
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

  logger.debug('Task %s is processing in %s' % (self.request.id, processingDir))

  imageCollection = models.ImageCollection.objects.get(id=imageCollectionId);
  imageList = imageCollection.images.all();
  
  #A Little bit of database logging
  oid = Order(processingDir=processingDir, imageCollection=imageCollection)
  oid.save()

  localImageList = [];
  
  for x in range(len(imageList)):
    #Download the image locally
    self.update_state(state='INITIALIZE', meta={'stage':'image fetch', 'i':x, 'total':len(imageList)})
    imageName = imageList[x].originalImageUrl;
    extension = os.path.splitext(imageName)[1]
    localName = path_join(processingDir, 'frame_%05d%s' % (x, extension)); 
    wget(imageName, localName)

    #Convert the image if necessary    
    if extension not in ['.jpg', '.pgm', '.ppm']:
      self.update_state(state='INITIALIZE', meta={'stage':'image convert', 'i':x, 'total':len(imageList)})
      #Add code here to converty to jpg for visual sfm
      if extension=='not implemented':
        newLocalName = os.path.splitext(localName)[0] + '.jpg';
        #stuff, maybe call gdal?
        localName = newLocalName;
      else:
        raise Exception('Unsuported file type');

    localImageList.append(localName);
  
  filenames = list(imageList.values_list('imageUrl'))
  logger.info('The image list is %s' % filenames)

  self.update_state(state='PROCESSING', meta={'stage':'generate match points'})
  generateMatchPoints(localImageList, path_join(processingDir, 'match.nvm'), logger=logger)
  
  self.update_state(state='PROCESSING', meta={'stage':'writing gcp points'})
  cameras = [];
  for image in imageList:
    if 1:
    #try:
      [K, T, llh] = getKTO(image);
      cameras.append({'image':image.id, 'K':K, 'tranformation':T, 'origin':llh})
    #except:
      pass

  #Make this a separate injest process, making CAMERAS linked to the images
  #data = arducopter.loadAdjTaggedMetadata(r'd:\visualsfm\arducopter\2014-03-20 13-22-44_adj_tagged_images.txt');
  #Make this read the cameras from the DB instead
  #writeGcpFileEnu(data, r'd:\visualsfm\arducopter\match.nvm.gcp', lat_origin=origin['lat'], lon_origin=origin['lon'], h_origin=origin['h'])

  #runSparse(r'd:\visualsfm\arducopter\match.nvm', r'd:\visualsfm\arducopter\sparse.nvm', gcp=True, shared=True)
  self.update_state(state='PROCESSING', meta={'stage':'sparse'})
  runSparse(path_join(processingDir, 'match.nvm'), path_join(processingDir, 'sparse.nvm'), gcp=False, shared=True, logger=logger)

  self.update_state(state='FINALIZE', meta={'stage':'loading resulting cameras'})
  
  
  cams = readNvm(path_join(processingDir, 'sparse.nvm'))
  cams.sort(key=lambda x:x.name)
  
  logger.info(str(cams[0]))

  return oid.id;