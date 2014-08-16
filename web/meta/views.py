from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from django.core import serializers
import meta.models

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
    imgs = meta.models.Image.objects.all();
    return HttpResponse( serializers.serialize('json', imgs) , content_type="application/json");

def fetchControlPointList(request):    
    geoPoints = meta.models.ControlPoint.objects.all();    
    return HttpResponse( serializers.serialize('geojson', geoPoints) , content_type="application/json");
    