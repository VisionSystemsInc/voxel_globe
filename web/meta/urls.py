from django.conf.urls import patterns, url

from meta import views

urlpatterns = patterns('',
# pages                       
    url(r'^$', views.index, name='index'),
    url(r'^imageIngest/$', views.imageIngest, name='imageIngest'),
    url(r'^tiePointCreator/$', views.tiePointCreator, name='tiePointCreator'),
    url(r'^voxelCreator/$', views.voxelCreator, name='voxelCreator'),
    url(r'^voxelWorldViewer/$', views.voxelWorldViewer, name='voxelWorldViewer'),

# json API calls    
    url(r'^fetchVideoList$', views.fetchVideoList, name='fetchVideoList'),
    url(r'^fetchControlPointList$', views.fetchControlPointList, name='fetchControlPointList'),
)