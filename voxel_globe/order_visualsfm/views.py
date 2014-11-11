from django.shortcuts import render
from django.http import HttpResponse

from ..meta import models

# Create your views here.
def make_order(request):
  image_collection_list = models.ImageCollection.objects.all()
  return render(request, 'order_visualsfm/html/order_list.html', 
                {'image_collection_list':image_collection_list})

def order(request, image_collection_id):
  image_collection = models.ImageCollection.objects.get(id=image_collection_id);
  image_list = image_collection.images;
  #Doesnm't work, I don't care. The UI isn't the point here
  
  #CALL THE CELERY TASK!
  return render(request, 'order_visualsfm/html/order.html', 
                {'image_list':image_list})
