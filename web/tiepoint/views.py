from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def tiePointCreator(request):
    return render(request, 'tiepoint/html/tiePointCreator.html')

def fetchCameraRay(request):
  import tiepoint_tasks
  
  points = tiepoint_tasks.fetchCameraRay(**request.REQUEST);
  
  return HttpResponse(points);

def fetchCameraFrustum(request):
  import tiepoint_tasks

  points = tiepoint_tasks.fetchCameraFrustum(**request.REQUEST);
  
  return HttpResponse(points);
