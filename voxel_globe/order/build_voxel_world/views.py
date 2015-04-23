from django.shortcuts import render
from django.http import HttpResponse

from uuid import uuid4

from voxel_globe.meta import models
from voxel_globe.meta.tools import getHistory
from .models import Session

# Create your views here.
def make_order_1(request):
  uuid = uuid4()
  session = Session(uuid=uuid, owner=request.user);
  session.save();

  image_collection_list = models.ImageCollection.objects.all();
  response = render(request, 'order/build_voxel_world/html/make_order_1.html', 
                {'image_collection_list':image_collection_list});
  response.set_cookie('order_build_voxel_world_uuid', uuid, max_age=15*60)
  return response

def make_order_2(request, image_collection_id):
  #Choose the scene
  scene_list = models.Scene.objects.all()

  return render(request, 'order/build_voxel_world/html/make_order_2.html',
                {'scene_list':scene_list,
                 'image_collection_id':image_collection_id})

def make_order_3(request, image_collection_id, scene_id):
  import voxel_globe.tools.enu as enu
  from voxel_globe.meta.tools import getLlh
  import numpy as np
  
  image_collection = models.ImageCollection.objects.get(id=image_collection_id)
  image_list = image_collection.images.all()
  #scene = models.Scene.objects.get(id=scene_id);

  llhs = []
  
  for image in image_list:
    llhs.append(getLlh(image.history()))

  llhs = np.array(llhs)
  lon_min, lat_min, alt_min = llhs.min(axis=0)
  lon_max, lat_max, alt_max = llhs.max(axis=0)    

  bbox = {'lon_min':lon_min,
          'lon_max':lon_max,
          'lat_min':lat_min,
          'lat_max':lat_max,
          'alt_min':alt_min,
          'alt_max':alt_max}
  
  return render(request, 'order/build_voxel_world/html/make_order_3.html',
                {'scene_id':scene_id, 'bbox':bbox,
                 'image_collection_id':image_collection_id})


def make_order_4(request, image_collection_id, scene_id):
  from voxel_globe.build_voxel_world import tasks
  
  try:
    uuid = request.COOKIES['order_build_voxel_world_uuid'];
    session = Session.objects.get(uuid=uuid);
    session.delete();
  except:
    response = HttpResponse('Session Expired')
    try:
      response.delete_cookie('order_build_voxel_world_uuid')
    finally:
      return response;

  history = getHistory(request.REQUEST.get('history', None))

  bbox = {'lat1': request.POST['lat1'], 
          'lon1': request.POST['lon1'], 
          'alt1': request.POST['alt1'], 
          'lat2': request.POST['lat2'], 
          'lon2': request.POST['lon2'], 
          'alt2': request.POST['alt2'],
          'vox': request.POST['vox']}
  
  skipFrames = int(request.POST['skip'])

  t = tasks.runBuildVoxelModel.apply_async(args=(image_collection_id, scene_id, bbox, skipFrames, True, history))

  #Crap ui filler   
  image_collection = models.ImageCollection.objects.get(id=image_collection_id);
  image_list = image_collection.images;
  #WARNING, Source of History error, but images shouldn't change!?
  scene = models.Scene.objects.get(id=scene_id);

  #CALL THE CELERY TASK!
  response = render(request, 'order/build_voxel_world/html/make_order_4.html', 
                   {'origin':scene.origin,
                    'image_list':image_list,
                    'task_id': t.task_id})
  response.delete_cookie('order_build_voxel_world_uuid')

  return response

def order_status(request, task_id):
  import urllib2, json, os
  from celery.result import AsyncResult
  
  task = AsyncResult(task_id);
  
  status = {'task': task};
 
  return render(request, 'order/build_voxel_world/html/order_status.html',
                status)
  #return HttpResponse('Task %s\n%s' % (task_id, status))
