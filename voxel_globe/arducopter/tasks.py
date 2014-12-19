import os
#import voxel_globe.tasks as tasks
from ..common_tasks import app, VipTask
from glob import glob
import voxel_globe.meta.models
from os import environ as env
from os.path import join as path_join

from django.contrib.gis import geos

from voxel_globe.angelfire.tasks import add_sample_cameras, add_sample_tie_point

import json;

import subprocess;

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__);

@app.task(base=VipTask, bind=True)
def ingest_data(self, uploadSession_id, imageDir):
  ''' task for the ingest route, to ingest the data an upload sessions points to '''
  import voxel_globe.ingest.models as IngestModels
  uploadSession = IngestModels.UploadSession.objects.get(id=uploadSession_id);
  directories = uploadSession.directory.all();
  #imageDirectory = directories.filter(name='image')
  #metaDirectory = directories.filter(name='meta')
  
  imageCollection = voxel_globe.meta.models.ImageCollection.create(name="Arducopter Upload %s" % uploadSession_id, service_id = self.request.id);
  imageCollection.save();
  
  
  for d in glob(os.path.join(imageDir, '*\\')):
    files = glob(os.path.join(d, '*.jpg'));
    files.sort()
    for f in files:
      zoomifyName = f[:-4] + '_zoomify'
      pid = subprocess.Popen(['vips', 'dzsave', f, zoomifyName, '--layout', 'zoomify'])
      pid.wait();
      
      relFilePath = os.path.relpath(f, env['VIP_IMAGE_SERVER_ROOT']).replace('\\', '/');
      basename = os.path.split(f)[-1]
      relZoomPath = os.path.relpath(zoomifyName, env['VIP_IMAGE_SERVER_ROOT']).replace('\\', '/');

      img = voxel_globe.meta.models.Image.create(
                             name="Arducopter Upload %s Frame %s" % (uploadSession_id, basename), 
                             imageWidth=4096, imageHeight=2160, 
                             numberColorBands=3, pixelFormat='b', fileFormat='zoom',
                             imageUrl='%s://%s:%s/%s/%s/' % (env['VIP_IMAGE_SERVER_PROTOCOL'], 
                                                             env['VIP_IMAGE_SERVER_HOST'], 
                                                             env['VIP_IMAGE_SERVER_PORT'], 
                                                             env['VIP_IMAGE_SERVER_URL_PATH'], 
                                                             relZoomPath),
                             originalImageUrl='%s://%s:%s/%s/%s' % (env['VIP_IMAGE_SERVER_PROTOCOL'], 
                                                                    env['VIP_IMAGE_SERVER_HOST'], 
                                                                    env['VIP_IMAGE_SERVER_PORT'], 
                                                                    env['VIP_IMAGE_SERVER_URL_PATH'], 
                                                                    relFilePath),
                             service_id = self.request.id);
      img.save();
     
      imageCollection.images.add(img);

@app.task(base=VipTask, bind=True)
def add_arducopter_images(self, *args, **kwargs):
  images = glob(path_join(env['VIP_PROJECT_ROOT'], 'images', '1fps*', ''));
  images.sort();
  imageCollection = [];
  for image in images:
    image = os.path.basename(os.path.dirname(image));
    frameNum = image[11:15]
    if voxel_globe.meta.models.Image.objects.filter(name="Arducopter Mission 2 Frame:%s" % frameNum):
      raise Exception('Already exists');
    img = voxel_globe.meta.models.Image.create(name="Arducopter Mission 2 Frame:%s" % frameNum, imageWidth=4096, imageHeight=2160, 
                             numberColorBands=3, pixelFormat='b', fileFormat='zoom', 
                             imageUrl='%s://%s:%s/%s/%s/' % (env['VIP_IMAGE_SERVER_PROTOCOL'], 
                                                             env['VIP_IMAGE_SERVER_HOST'], 
                                                             env['VIP_IMAGE_SERVER_PORT'], 
                                                             env['VIP_IMAGE_SERVER_URL_PATH'], 
                                                             image),
                             originalImageUrl='%s://%s:%s/%s/%s.jpg' % (env['VIP_IMAGE_SERVER_PROTOCOL'], 
                                                                        env['VIP_IMAGE_SERVER_HOST'], 
                                                                        env['VIP_IMAGE_SERVER_PORT'], 
                                                                        env['VIP_IMAGE_SERVER_URL_PATH'], 
                                                                        image),
                             service_id = self.request.id);
    img.save();
     
    imageCollection.append(img.id);
     
  ic = voxel_globe.meta.models.ImageCollection.create(name="Arducopter Mission 2", service_id = self.request.id);
  ic.save();
  ic.images.add(*imageCollection);

  ic = voxel_globe.meta.models.ImageCollection.create(name="Arducopter Mission 2 short", service_id = self.request.id);
  ic.save();
  ic.images.add(*imageCollection[101:151]);
   
  with open(path_join(env['VIP_PROJECT_ROOT'], 'images', 'Contractor_Survey_NorthA_List.csv'), 'r') as fid:
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
       
    tp = voxel_globe.meta.models.ControlPoint.create(name=name,
                                         description=desc,
                                         point=point,
                                         apparentPoint=point)
    tp.service_id = self.request.id;
    tp.save();

  print '********** Populating arducopter cameras **********'     
  add_sample_cameras(self, path_join(env['VIP_PROJECT_ROOT'], 'images', 'cannon_cameras_gps.txt'), srid=7428)
  
  voxel_globe.meta.models.Scene.create(name="Arducopter Mission 2 origin", service_id = self.request.id,
                                       origin='SRID=%d;POINT(%0.12f %0.12f %0.12f)' % (7428, -92.215197, 37.648858, 300)).save()
