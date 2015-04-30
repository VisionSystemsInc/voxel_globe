from ..common_tasks import app, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
import logging

import os

@app.task(base=VipTask, bind=True)
def runBuildVoxelModel(self, imageCollectionId, sceneId, bbox, skipFrames, cleanup=True, history=None):
  from vsi.tools.redirect import Redirect, Logger as LoggerWrapper
  with Redirect(stdout_c=LoggerWrapper(logger, lvl=logging.INFO), stderr_c=LoggerWrapper(logger, lvl=logging.WARNING)):  
    from voxel_globe.meta import models
    from voxel_globe.meta.tools import getKrt
    import voxel_globe.tools

    from boxm2_scene_adaptor import boxm2_scene_adaptor

    from vil_adaptor import load_image
    from vpgl_adaptor import load_perspective_camera
    from voxel_globe.tools.wget import download as wget
    
    from vsi.vxl.create_scene_xml import create_scene_xml 
    
    openclDevice = os.environ['VIP_OPENCL_DEVICE']
    
    scene = models.Scene.objects.get(id=sceneId)
    
    imageCollection = models.ImageCollection.objects.get(id=imageCollectionId).history(history);
    imageList = imageCollection.images.all();
    
    processingDir = voxel_globe.tools.getTaskDir()
  
    logger.warning(bbox)
    
    create_scene_xml(openclDevice, 3, float(bbox['vox']), 
                     (float(bbox['lon1']), float(bbox['lat1']), float(bbox['alt1'])), 
                     (float(bbox['lon2']), float(bbox['lat2']), float(bbox['alt2'])),
                     origin=scene.origin,
                     output_file=open(os.path.join(processingDir, 'scene.xml'), 'w'), 
                     model_dir='.', num_bins=1)
#     create_scene_and_blocks(processingDir, app_model, obs_model,
#                             scene.origin[0], scene.origin[1], scene.origin[2],
#                             float(bbox['lon1']), float(bbox['lat1']), float(bbox['alt1']),
#                             float(bbox['lon2']), float(bbox['lat2']), float(bbox['alt2']),
#                             float(bbox['vox']), block_len_xy, block_len_z, "utm", 1, 'scene');
    
    counter = 1;
    
    imageNames = []
    cameraNames = []
    
    #Prepping
    for image in imageList:
      self.update_state(state='INITIALIZE', meta={'stage':'image fetch', 'i':counter, 'total':len(imageList)})
      image = image.history(history)
      (K,R,T,o) = getKrt(image.history(history), history=history)
      
      krtName = os.path.join(processingDir, 'frame_%05d.krt' % counter)
      
      with open(krtName, 'w') as fid:
        print >>fid, (("%0.18f "*3+"\n")*3) % (K[0,0], K[0,1], K[0,2], K[1,0], K[1,1], K[1,2], K[2,0], K[2,1], K[2,2]);
        print >>fid, (("%0.18f "*3+"\n")*3) % (R[0,0], R[0,1], R[0,2], R[1,0], R[1,1], R[1,2], R[2,0], R[2,1], R[2,2]);
  
        print >>fid, ("%0.18f "*3+"\n") % (T[0,0], T[1,0], T[2,0]);
      
      imageName = image.originalImageUrl;
      extension = os.path.splitext(imageName)[1]
      localName = os.path.join(processingDir, 'frame_%05d%s' % (counter, extension)); 
      wget(imageName, localName, secret=True)
      
      counter += 1;
    
      imageNames.append(localName)
      cameraNames.append(krtName)
      
    variance = 0.06
    
    scene = boxm2_scene_adaptor(os.path.join(processingDir, "scene.xml"),  openclDevice);
  
    current_level = 0;
  
    loaded_imgs = [];
    loaded_cams = [];
  
    for i in range(0, len(imageNames), skipFrames):
      logger.debug("i: %d img name: %s cam name: %s", i, imageNames[i], cameraNames[i])
      self.update_state(state='PRELOADING', meta={'stage':'image load', 'i':i, 'total':len(imageNames)})
      img, ni, nj = load_image(imageNames[i])
      loaded_imgs.append(img)
      pcam = load_perspective_camera(cameraNames[i])
      loaded_cams.append(pcam)
  
    refine_cnt = 5;
    for rfk in range(0, refine_cnt, 1):
      for idx, (img, cam) in enumerate(zip(loaded_imgs, loaded_cams)):
        self.update_state(state='PROCESSING', meta={'stage':'update', 'i':rfk+1, 'total':refine_cnt, 'image':idx+1, 'images':len(loaded_imgs)})
        logger.debug("refine_cnt: %d, idx: %d", rfk, idx)
        scene.update(cam,img,True,True,None,openclDevice[0:3],variance,tnear = 1000.0, tfar = 100000.0);
  
      scene.write_cache();
      
      if rfk < refine_cnt-1:
        self.update_state(state='PROCESSING', meta={'stage':'refine', 'i':rfk, 'total':refine_cnt})
        logger.debug("refining %d...", rfk)
        scene.refine(0.3, openclDevice[0:3]);
        scene.write_cache();
        
    ''' The rest of this is crap preview code '''
    
    from distutils.dir_util import mkpath
    import tempfile
    ingestDir = tempfile.mkdtemp(dir=os.environ['VIP_IMAGE_SERVER_ROOT']);
    os.chmod(ingestDir, 0775)
    expectedDir = os.path.join(ingestDir, 'preview')
    mkpath(expectedDir)
    renderFlyThrough(scene, expectedDir, 1024, 1024)
    
    from voxel_globe.no_metadata.tasks import ingest_data
    from voxel_globe.ingest.models import UploadSession
    import django.contrib.auth.models
    some_owner_id = django.contrib.auth.models.User.objects.all()[0].id 
    uploadSession = UploadSession.objects.create(name='Voxel preview %s' %imageCollection.name, 
                                                 owner_id=some_owner_id) #sacrificial uploadSession
    ingest_data.apply(args=(uploadSession.id, ingestDir))


def renderFlyThrough(scene, outDir, width, height):
  from boxm2_adaptor import init_trajectory,trajectory_next
  from boxm2_scene_adaptor import persp2gen, stretch_image, save_image
  from boxm2_register import remove_data
  startInc = 45.0                        #start incline angle off nadir
  endInc = 45.0                          #end incline angle off nadir
  radius   = -1.0                        #radius -1 defaults to half width of the volume

  trajectory = init_trajectory(scene.scene, startInc, endInc, radius, width, height)
  min_value = 0.0 
  max_value = 1.0
  
  increments = 10
  counter = 1
  for x in range(0, 500, 1):
    prcam = trajectory_next(trajectory)
    if x % increments == 0:
      expimg = scene.render(prcam, width, height)
      expimg_s = stretch_image(expimg, min_value, max_value, 'byte')
      save_image(expimg_s, os.path.join(outDir, 'expected_%05d.tif'%counter))
      remove_data(expimg.id)
      counter += 1
    remove_data(prcam.id)


