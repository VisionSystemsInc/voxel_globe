from ..common_tasks import app, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

import os

@app.task(base=VipTask, bind=True)
def runBuildVoxelModel(self, imageCollectionId, sceneId, bbox, cleanup=True, history=None):
  from voxel_globe.meta import models
  from voxel_globe.meta.tools import getKrt
  import voxel_globe.tools
  
  from boxm2_scene_adaptor import create_scene_and_blocks,boxm2_scene_adaptor
  
  from vil_adaptor import load_image
  from vpgl_adaptor import load_perspective_camera
  from voxel_globe.tools.wget import download as wget
  
  scene = models.Scene.objects.get(id=sceneId)
  
  imageCollection = models.ImageCollection.objects.get(id=imageCollectionId).history(history);
  imageList = imageCollection.images.all();
  
  processingDir = voxel_globe.tools.getTaskDir()

  app_model = "boxm2_mog3_grey"
  obs_model = "boxm2_num_obs"
  block_len_xy = 100
  block_len_z = 60
  create_scene_and_blocks(processingDir, app_model, obs_model,
                          scene.origin[0], scene.origin[1], scene.origin[2],
                          float(bbox['lon1']), float(bbox['lat1']), float(bbox['alt1']),
                          float(bbox['lon2']), float(bbox['lat2']), float(bbox['alt2']),
                          float(bbox['vox']), block_len_xy, block_len_z, "utm", 1, 'scene');
  
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
  
  scene = boxm2_scene_adaptor(os.path.join(processingDir, "scene.xml"),  "gpu1");

  current_level = 0;

  loaded_imgs = [];
  loaded_cams = [];

  for i in range(len(imageNames)):
    #print "i: %d img name: %s cam name: %s" % (i, imgs[i], cams[i]);
    self.update_state(state='PRELOADING', meta={'stage':'image load', 'i':i, 'total':len(imageNames)})
    img, ni, nj = load_image(imageNames[i]);
    loaded_imgs.append(img);
    pcam = load_perspective_camera(cameraNames[i]);
    loaded_cams.append(pcam);

  refine_cnt = 4;
  for rfk in range(0, refine_cnt, 1):
    frames = range(rfk,len(loaded_cams),5);

    for idx, i in enumerate(frames):
      print "refine_cnt: %d, idx: %d, i: %d" % (rfk, idx, i);
      scene.update(loaded_cams[i],loaded_imgs[i],True,True,None,"gpu",variance); # update_alpha=True, update_app = True, mask=None

    scene.write_cache();
    
    if rfk < refine_cnt-1:
      print "refining..";
      scene.refine(0.3, "gpu1");
      scene.write_cache();

