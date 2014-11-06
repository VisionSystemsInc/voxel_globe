from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def tiePointCreator(request):
    return render(request, 'tiepoint/html/tiePointCreator.html')

def fetchCameraRay(request):
  import vip.tiepoint_app.tasks
  
  points = vip.tiepoint_app.tasks.fetchCameraRay(**request.REQUEST);
  
  return HttpResponse(points);

def fetchCameraFrustum(request):
  import vip.tiepoint_app.tasks

  points = vip.tiepoint_app.tasks.fetchCameraFrustum(**request.REQUEST);
  
  return HttpResponse(points);
