from django.shortcuts import render
from django.http import HttpResponse

from ...meta import models
from ...meta.tools import getHistory

# Create your views here.
def make_order(request):
  image_collection_list = models.ImageCollection.objects.all()
  return render(request, 'order/visualsfm/html/order_list.html', 
                {'image_collection_list':image_collection_list})

def order(request, image_collection_id):
  from ...visualsfm import tasks
  
  history = getHistory(request.REQUEST.get('history', None))

  t = tasks.runVisualSfm.apply_async(args=(image_collection_id, history))

  #Crap ui filler   
  image_collection = models.ImageCollection.objects.get(id=image_collection_id);
  image_list = image_collection.images;
  #WARNING, Source of History error, but images shouldn't change!?
  
  #CALL THE CELERY TASK!
  return render(request, 'order/visualsfm/html/order.html', 
                {'image_list':image_list, 'taskid':t.task_id})
