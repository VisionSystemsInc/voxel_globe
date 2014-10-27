from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from .forms import UploadFileForm

from ingest import models

### Rest API setup
import ingest.serializers
import rest_framework.routers
import rest_framework.viewsets
router = rest_framework.routers.DefaultRouter()
class IngestViewSet(rest_framework.viewsets.ModelViewSet):
  filter_backends = (rest_framework.filters.DjangoFilterBackend,);
  filter_fields = ['id'];#map(lambda x: x[0].name, meta.models.TiePoint._meta.get_fields_with_model());
def ViewSetFactory(model, serializer):
  return type('ViewSet_%s' % model._meta.model_name, (IngestViewSet,), {'queryset':model.objects.all(), 'serializer_class':serializer})

for m in [models.UploadSession, models.Directory, models.File]:
  router.register(m._meta.model_name, ViewSetFactory(m, ingest.serializers.serializerFactory(m)))


def ingest(request):
  return render(request, 'ingest/html/ingest.html')

def blah(request):
  if request.method=='POST':
    form = UploadFileForm(request.POST, request.FILES);
    if form.is_valid():
      return HttpResponse('form valid');
  else:
    form = UploadFileForm();
  
  #return render(request, 'ingest/html/upload.html', {'form':form})
  return render_to_response('ingest/html/upload.html', {'form':form}, context_instance=RequestContext(request))
  
def upload(request):
  return HttpResponse('ok' + str(request.FILES));