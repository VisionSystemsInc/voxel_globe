from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from .forms import UploadFileForm

from voxel_globe.ingest import models

### Rest API setup
import voxel_globe.ingest.serializers
import rest_framework.routers
import rest_framework.viewsets
router = rest_framework.routers.DefaultRouter()

class IngestViewSet(rest_framework.viewsets.ModelViewSet):
  filter_backends = (rest_framework.filters.DjangoFilterBackend,);
  filter_fields = ['id', 'name']#, 'directory', 'file'];
  def pre_save(self, obj):
    obj.owner = self.request.user;
    super(IngestViewSet, self).pre_save(obj);
  def get_queryset(self):
    return super(IngestViewSet, self).get_queryset().filter(owner=self.request.user);
  
def ViewSetFactory(model, serializer):
  return type('ViewSet_%s' % model._meta.model_name, (IngestViewSet,), {'queryset':model.objects.all(), 'serializer_class':serializer})

router.register(models.File._meta.model_name, ViewSetFactory(models.File, voxel_globe.ingest.serializers.FileSerializer))
router.register(models.Directory._meta.model_name, ViewSetFactory(models.Directory, voxel_globe.ingest.serializers.DirectorySerializer))
router.register(models.Directory._meta.model_name+'_nest', ViewSetFactory(models.Directory, voxel_globe.ingest.serializers.NestFactory(voxel_globe.ingest.serializers.DirectorySerializer)))
router.register(models.UploadSession._meta.model_name, ViewSetFactory(models.UploadSession, voxel_globe.ingest.serializers.UploadSessionSerializer));
router.register(models.UploadSession._meta.model_name+'_nest', ViewSetFactory(models.UploadSession, voxel_globe.ingest.serializers.NestFactory(voxel_globe.ingest.serializers.UploadSessionSerializer)));

def ingest(request):
  return render(request, 'ingest/html/ingest.html')

def blah(request):
  uploadSession = models.UploadSession(name='Blah', owner=request.user);
  uploadSession.save();
  directory = models.Directory(name='Blahdir', session=uploadSession, owner=request.user);
  directory.save();
  testFile = models.File(name='Blahfile', directory=directory, owner=request.user);
  testFile.save();
  
  if request.method=='POST':
    form = UploadFileForm(request.POST, request.FILES);
    if form.is_valid():
      return HttpResponse('form valid');
  else:
    form = UploadFileForm();

  #return render(request, 'ingest/html/upload.html', {'form':form})
  return render_to_response('ingest/html/upload.html', 
                            {'form':form,
                             'uploadSession':uploadSession,
                             'directory':directory,
                             'testFile':testFile}, 
                            context_instance=RequestContext(request))
  
def upload(request):
  uploadSession_id = request.POST['uploadSession']
  directory_id = request.POST['directory']
  testFile_id = request.POST['testFile']
  
  s = 'ok<br>'
  import os
  os.mkdir(r'd:\vip\tmp\%s' % uploadSession_id)
  os.mkdir(r'd:\vip\tmp\%s\%s' % (uploadSession_id, directory_id))
  for f in request.FILES:
    s += request.FILES[f].name
    with open(r'd:\vip\tmp\%s\%s\%s' % (uploadSession_id, directory_id, request.FILES[f].name), 'wb') as fid:
      for c in request.FILES[f].chunks():
        fid.write(c)
  
  return HttpResponse(s);