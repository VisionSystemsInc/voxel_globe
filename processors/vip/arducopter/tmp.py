import os
import vip.tasks as tasks
from glob import glob
import meta.models
from os import environ as env
from os.path import join as path_join

from django.contrib.gis import geos

from add_purdue_data import add_sample_cameras, add_sample_tie_point

import json;

@tasks.app.task(base=tasks.VipTask, bind=True)
def add_arducopter_images(self, *args, **kwargs):
  images = glob(path_join(env['VIP_PROJECT_ROOT'], 'images', '1fps*', ''));
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
       
    tp = meta.models.ControlPoint.create(name=name,
                                         description=desc,
                                         point=point,
                                         apparentPoint=point)
    tp.service_id = self.request.id;
    tp.save();
  print '********** Populating arducopter cameras **********'     
  add_sample_cameras(self, path_join(env['VIP_PROJECT_ROOT'], 'images', 'cannon_cameras_1.txt')) #history = 1
  add_sample_cameras(self, path_join(env['VIP_PROJECT_ROOT'], 'images', 'cannon_cameras_2.txt'), srid=7428) #history = 1

if __name__ == '__main__':
  import django;
  django.setup();
   
  print '********** Populating arducopter images **********'
  t = add_arducopter_images.apply();
  if t.failed():
    raise t.result

  print '********** Populating arducopter tiepoints **********'
  t = add_sample_tie_point.apply(args=(os.path.join(env['VIP_PROJECT_ROOT'], 'images', 'arducopter_tie_points.xml'),
                                       os.path.join(env['VIP_PROJECT_ROOT'], 'images', 'arducopter_control_points.txt'),
                                       None,
                                       range(519)));
  if t.failed():
    raise t.result
