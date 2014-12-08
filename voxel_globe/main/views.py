from django.shortcuts import render
# Create your views here. Mostly placeholders
from django.contrib.auth.models import User

def index(request):
    try:
      user = User.objects.get(username=request.META['REMOTE_USER'], is_active=True)
    except:
      user= None
    return render(request, 'main/html/index.html',
                  {'user':user})

def voxelCreator(request):
    return render(request, 'main/html/voxelCreator.html')

def voxelWorldViewer(request):
    return render(request, 'main/html/voxelWorldViewer.html')
