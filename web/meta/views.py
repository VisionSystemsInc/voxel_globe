from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from django.core import serializers
import meta.models
import json

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
    return HttpResponse( serializers.serialize('json', imgs) , content_type="application/json")

def fetchImages(request):
    print("Requested images for video collection id ", request.REQUEST["videoId"])
    videoId = request.REQUEST["videoId"]
    video = meta.models.ImageCollection.objects.get(id=int(videoId))
# ANDY - Add code to grab and return the list of image objects specified by the video.images contents
    res = {}
    res['error'] = "not implemented - add code to grab image list for video id " + videoId
    return HttpResponse( json.dumps(res), content_type="application/json")
    
def fetchControlPointList(request):    
    geoPoints = meta.models.ControlPoint.objects.all()    
    return HttpResponse( serializers.serialize('geojson', geoPoints) , content_type="application/json")
  
def fetchTiePoints(request):    
    print("Requested tie points for image id ", request.REQUEST["imageId"])
    imageId = request.REQUEST["imageId"]
# ANDY - Add code to grab and return the list of tie points for an image with ID imageId
# I will take care of filtering based on control point selection in the UI (for now)
    res = {}
    res['error'] = "not implemented - add code to grab tie points for image id " + imageId
    return HttpResponse( json.dumps(res), content_type="application/json")
     
#  API for updating data in the database
def createTiePoint(request):
    print("Requested to create a tie points for image id ", request.REQUEST["imageId"], 
          " associated with control point ", request.REQUEST["controlPointId"], 
          " with x=", request.REQUEST["x"], " and y=", request.REQUEST["y"])
# ANDY - Create an object in the tie point table with the appropriate fields 
    return 

def updateTiePoint(request):
    print("Requested to update a tie point with id ", request.REQUEST["tiePointId"],           
          " with x=", request.REQUEST["x"], " and y=", request.REQUEST["y"])    
# ANDY - Update the tie point table with the appropriate values
    return 
