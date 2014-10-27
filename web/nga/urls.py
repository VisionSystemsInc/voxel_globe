from django.conf.urls import patterns, include, url

from django.contrib import admin

#handler400 = 'world.views.error400page'
#AEN: THIS doesn't work!

import main.views

urlpatterns = patterns('',
    #Admin site apps
    url(r'^admin/', include(admin.site.urls)),
    #Test app for development reasons
    url(r'^world/', include('world.urls', namespace='world')),
    
    # pages
    #Main home page    
    url(r'^$', main.views.index, name='index'),
    #Placeholders
#    url(r'^apps/imageIngest/$', main.views.imageIngest, name='imageIngest'),
    url(r'^apps/voxelCreator/$', main.views.voxelCreator, name='voxelCreator'),
    url(r'^apps/voxelWorldViewer/$', main.views.voxelWorldViewer, name='voxelWorldViewer'),
#    url(r'^apps/ingest/upload$', 'ingest.views.upload', name="uploadEndpoint"),
#    url(r'^apps/ingest/$', 'ingest.views.blah'),

    #REST auth endpoint
    #url(r'^rest/', include('rest_framework.urls', namespace='rest_framework')),

    #apps
    url(r'^meta/', include('meta.urls', namespace='meta')),
    url(r'^apps/tiepoint/', include('tiepoint.urls', namespace='tiepoint')),
    url(r'^apps/ingest/', include('ingest.urls', namespace='ingest')),
)
