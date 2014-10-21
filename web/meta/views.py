from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from django.core import serializers
import meta.models
import tiepoint_tasks

import rest_framework.filters
import rest_framework.status
import rest_framework.response
import rest_framework.mixins
import rest_framework.views
import rest_framework.viewsets
import rest_framework.routers

import meta.serializers

import inspect

class AutoViewSet(rest_framework.mixins.CreateModelMixin,
                  rest_framework.mixins.RetrieveModelMixin,
                  rest_framework.mixins.UpdateModelMixin,
                  rest_framework.mixins.ListModelMixin,
                  rest_framework.viewsets.GenericViewSet):
  filter_backends = (rest_framework.filters.DjangoFilterBackend,);
  filter_fields = map(lambda x: x[0].name, meta.models.TiePoint._meta.get_fields_with_model());
  
  def destroy(self, request, pk=None, *args, **kwargs):
    ''' Destroy that sets delete to true, but does not actually delete to support history'''
    try:
      obj = self.get_queryset().get(pk=pk).history();
      #obj = meta.models.TiePoint.objects.get(id=tiePointId).history();
      #Get the latest version of that tiepoint
      obj.deleted = True;
      super(obj._meta.model, obj).save();
      #Do not use the VIPModel save, since this is a strict change in a status flag
      return rest_framework.response.Response(status=rest_framework.status.HTTP_204_NO_CONTENT)
    except:
      #pk may have been None, or obj may have been None.
      return rest_framework.response.Response(status=rest_framework.status.HTTP_400_BAD_REQUEST);

#  def list(self, request):
#    print 'LIST';
#    #Called by main endpoint GET, to list (a page if) the objects

#  def retrieve(self, request, pk=None):
#    print 'RETREIVE';
#    #Called by the individual id endpoint GET
  
#  def create(self, request):
#    print 'CREATE';
#    Called by main endpoint POST

#  def update(self, request, pk=None):
#    print 'UPDATE';
#    #Individual id endpoint PUT
    
#  def partial_update(self, request, pk=None):
#    print 'PARTIAL_UPDATE'
#    #Individual id endpoint PATCH


def ViewSetFactory(model, serilizer):
  return type('AutoViewSet_%s' % model._meta.model_name, (AutoViewSet,), {'queryset':model.objects.all(), 'serializer_class':serilizer})
  

#Define custom view sets here

auto_router = rest_framework.routers.DefaultRouter()
router = rest_framework.routers.DefaultRouter()

import rest_framework.generics

class TiePointViewSet(rest_framework.viewsets.ModelViewSet):
  queryset = meta.models.TiePoint.objects.all();
  serializer_class = meta.serializers.TiePointSerializer;
#  filter_backends = (rest_framework.filters.SearchFilter,);
  filter_fields = ['id', 'objectId', 'newerVersion'];
  filter_backends = (rest_framework.filters.DjangoFilterBackend,);
#  filter_fields = map(lambda x: x[0].name, meta.models.TiePoint._meta.get_fields_with_model())+['newerVersion__isnull'];
  
  def destroy(self, request, pk=None):
    print 'DESTROY!DESTROY!DESTROY!DESTROY!'
    import rpdb2; rpdb2.start_embedded_debugger('vsi');
  def get_queryset(self):
    if self.request.QUERY_PARAMS.has_key('newestVersion'):
      return super(TiePointViewSet, self).get_queryset().filter(newerVersion=None);
    else:
      return super(TiePointViewSet, self).get_queryset();

router.register('tiepoint', TiePointViewSet);
#Either register custom serializers here
#May need to add if to for loop to check if already registered

''' Create serializers for all VIP object models '''
for m in inspect.getmembers(meta.models):
  if inspect.isclass(m[1]):
    if issubclass(m[1], meta.models.VipObjectModel) and not m[1] == meta.models.VipObjectModel:
      #pass
      auto_router.register(m[1]._meta.model_name, ViewSetFactory(m[1], meta.serializers.serializerFactory(m[1])))

#Either register custom serializers or here. I won't know which is right until I try
      
def index(request):
    return render(request, 'meta/html/index.html')

def imageIngest(request):
    return render(request, 'meta/html/imageIngest.html')

def tiePointCreator(request):
    return render(request, 'meta/html/tiePointCreator.html')

def voxelCreator(request):
    return render(request, 'meta/html/voxelCreator.html')

def voxelWorldViewer(request):
    return render(request, 'meta/html/voxelWorldViewer.html')

#
# API for grabbing data in the database
#
def fetchVideoList(request):
    imgs = meta.models.ImageCollection.objects.all()
    return HttpResponse( serializers.serialize('geojson', imgs) , content_type="application/json")

def fetchImages(request):
  try:
    videoId = request.REQUEST["videoId"]
    video = meta.models.ImageCollection.objects.get(id=videoId)
#    return HttpResponse( serializers.serialize('geojson', video.images.all(), fields=('name',)), 
#                         content_type="application/json")
    return HttpResponse( serializers.serialize('geojson', video.images.all()), 
                         content_type="application/json")
    #based off of video_list_example.ipynb
  except meta.models.ImageCollection.DoesNotExist:
    return HttpResponse('')
    
def fetchControlPointList(request):    
    geoPoints = meta.models.ControlPoint.objects.all()    
    return HttpResponse( serializers.serialize('geojson', geoPoints) , content_type="application/json")
  
def fetchTiePoints(request):
  imageId = request.REQUEST["imageId"]
  tiePoints = meta.models.TiePoint.objects.filter(image_id=imageId, newerVersion=None, deleted=False)
  serializers.serialize('geojson', tiePoints, fields=('name', 'point', 'geoPoint'))
  return HttpResponse( serializers.serialize('geojson', tiePoints, fields=('name', 'point', 'geoPoint')) , content_type="application/json")
     
#  API for updating data in the database
def createTiePoint(request):
    imageId = request.REQUEST["imageId"];
    if 'controlPointId' in request.REQUEST:
      controlPointId = request.REQUEST["controlPointId"];
    else:
      controlPointId = None;
    x = request.REQUEST["x"];
    y = request.REQUEST["y"];
    name = request.REQUEST["name"];
    tiepoint_tasks.addTiePoint.apply(kwargs={'point':'POINT(%s %s)' % (x,y), 
                                    'image_id':imageId, 
                                    'geoPoint_id':controlPointId,
                                    'name': name});
    return HttpResponse('');

def updateTiePoint(request):
    print("Requested to update a tie point with id ", request.REQUEST["tiePointId"],           
          " with x=", request.REQUEST["x"], " and y=", request.REQUEST["y"])    

    tiepoint_tasks.updateTiePoint.apply(args=(request.REQUEST["tiePointId"], request.REQUEST["x"], request.REQUEST["y"]))
    #Eventually when the REAL update function is written, it may be EASIEST to say
    #"POINT(%s %s)" % (x, y), but until this is complete, it does not matter to me.
          
    return HttpResponse('');

def deleteTiePoint(request):
  tiePointId = request.REQUEST['id']
  object = meta.models.TiePoint.objects.get(id=tiePointId).history();
  #Get the latest version of that tiepoint
  object.deleted = True;
  super(object._meta.model, object).save();
  #Do not use the VIPModel save, since this is a strict change in a status flag
  return HttpResponse('');
  
def fetchCameraRay(request):
  points = tiepoint_tasks.fetchCameraRay(**request.REQUEST);
  
  return HttpResponse(points);

def fetchCameraFrustum(request):
  points = tiepoint_tasks.fetchCameraFrustum(**request.REQUEST);
  
  return HttpResponse(points);

def ingestArducopterData(request):
  import os
  from os import environ as env
  t = tiepoint_tasks.add_arducopter_images.apply();
  if t.failed():
    raise t.result
    
  t = tiepoint_tasks.add_sample_tie_point.apply(args=(os.path.join(env['VIP_DATABASE_DIR'], 'arducopter_tie_points.xml'),
                                             os.path.join(env['VIP_DATABASE_DIR'], 'arducopter_control_points.txt'),
                                             None,
                                             range(519)));
  if t.failed():
    raise t.result

#   t = tiepoint_tasks.update_sample_tie_point.apply(args=(os.path.join(env['VIP_DATABASE_DIR'], 'arducopter_tie_points.txt'),));
#   if t.failed():
#     raise t.result
# Too much is different for this to work, and quite frankly, I don't care!

  
  return HttpResponse('Success');