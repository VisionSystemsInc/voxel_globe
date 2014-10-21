from django.conf.urls import patterns, url, include
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
    url(r'^fetchTiePoints$', views.fetchTiePoints, name='fetchTiePoints'),
    url(r'^fetchImages$', views.fetchImages, name='fetchImages'),
    url(r'^fetchCameraRay$', views.fetchCameraRay, name='fetchCameraRay'),
    url(r'^fetchCameraFrustum$', views.fetchCameraFrustum, name='fetchCameraFrustum'),
    
    url(r'^ingestArducopterData$', views.ingestArducopterData, name='ingestArducopterData'),
    
#   modifications to data
    url(r'^createTiePoint$', views.createTiePoint, name='createTiePoint'),
    url(r'^updateTiePoint$', views.updateTiePoint, name='updateTiePoint'),
    url(r'^deleteTiePoint$', views.deleteTiePoint, name='deleteTiePoint'),

#   RESTful end points
    url(r'^rest/', include(views.router.urls)),
    url(r'^rest/auto/', include(views.auto_router.urls)),
)