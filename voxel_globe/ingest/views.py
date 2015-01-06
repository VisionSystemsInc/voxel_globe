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

import distutils.dir_util
import os

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

def chooseSession(request):
    return render_to_response('ingest/html/chooseSession.html', 
                            {'sensorTypes': models.SENSOR_TYPES}, 
                            context_instance=RequestContext(request))

def addFiles(request):
  upload_session_id = int(request.GET['upload'])
  uploadSession = models.UploadSession.objects.get(id=upload_session_id)
  
  #Temporary code only. This will get one directory successfully, or create a new one.
  try:
    directory = uploadSession.directory.get()
  except:
    directory = models.Directory(name='Blahdir', session=uploadSession, owner=request.user);
    directory.save();
    directory.name = str(directory.id); directory.save();
  testFile = models.File(name='Blahfile', directory=directory, owner=request.user);
  testFile.save();

  return render_to_response('ingest/html/addFiles.html',
                           {'uploadSession':uploadSession,
                            'directory':directory,
                            'testFile':testFile}, 
                            context_instance=RequestContext(request))

def blah(request):
  uploadSession = models.UploadSession(name='Blah', owner=request.user);
  uploadSession.save();
  uploadSession.name = str(uploadSession.id); uploadSession.save();
  directory = models.Directory(name='Blahdir', session=uploadSession, owner=request.user);
  directory.save();
  directory.name = str(directory.id); directory.save();
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
  try:
    uploadSession_id = request.POST['uploadSession']
  except:
    uploadSession = models.UploadSession(name='failesafe', owner=request.user)
    uploadSession.save();
    uploadSession.name = str(uploadSession.id); uploadSession.save();
    uploadSession_id = uploadSession.id
  try:
    directory_id = request.POST['directory']
  except:
    directory_id = 'failsafe'
  try:
    testFile_id = request.POST['testFile']
  except:
    testFile_id = 'failsafe'

  s = 'ok<br>'
  
  saveDir = os.path.join(os.environ['VIP_TEMP_DIR'], str(uploadSession_id), str(directory_id))
  distutils.dir_util.mkpath(saveDir)
  
  for f in request.FILES:
    s += request.FILES[f].name
    with open(os.path.join(saveDir, request.FILES[f].name), 'wb') as fid:
      for c in request.FILES[f].chunks():
        fid.write(c)
  
  return HttpResponse(s);

def ingestFolder(request):
  uploadSession_id = request.POST['uploadSession']
  #directories = models.Directory.objects.filter(uploadSession_id = uploadSession_id)
  #Code not quite done, using failsafe for now. 
  uploadSession = models.UploadSession.objects.get(id=uploadSession_id);

  sessionDir = os.path.join(os.environ['VIP_TEMP_DIR'], str(uploadSession.id))
  imageDir = os.path.join(os.environ['VIP_IMAGE_SERVER_ROOT'], str(uploadSession.id))
  if os.path.exists(imageDir):
    import tempfile
    imageDir = tempfile.mkdtemp(dir=os.environ['VIP_IMAGE_SERVER_ROOT']);
  
  print sessionDir, imageDir
  #TODO: The following should be a celery task too, and the two should be a 
  #workflow, and this plus ingest_data should be a workflow

  from glob import glob  
  metadata = glob(sessionDir+'/*/*_adj_tagged_images.txt');
  
  distutils.dir_util.copy_tree(sessionDir, imageDir)
  distutils.dir_util.remove_tree(sessionDir)
  
  if len(metadata)>0:
    import voxel_globe.arducopter.tasks;
    task = voxel_globe.arducopter.tasks.ingest_data.delay(uploadSession_id, imageDir);
  else:
    import voxel_globe.jpg_exif.tasks;
    task = voxel_globe.jpg_exif.tasks.ingest_data.delay(uploadSession_id, imageDir);

  return render(request, 'ingest/html/ingest_started.html', 
                {'task_id':task.task_id})