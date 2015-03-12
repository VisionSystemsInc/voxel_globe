from django.shortcuts import render

from uuid import uuid4

# Create your views here.
def make_order_1(request):
  uuid = uuid4()
  response = render(request, 'order/build_voxel_world/html/make_order_1.html', {'stuff':[1,2,3], 'uuid':uuid})
  response.set_cookie('order_build_voxel_world', uuid, max_age=15*60)
  return response
