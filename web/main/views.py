from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here. Mostly placeholders

def index(request):
    return render(request, 'main/html/index.html')

def imageIngest(request):
    return render(request, 'main/html/imageIngest.html')

def voxelCreator(request):
    return render(request, 'main/html/voxelCreator.html')

def voxelWorldViewer(request):
    return render(request, 'main/html/voxelWorldViewer.html')
