from django.conf.urls import patterns, url, include
from ingest import views

urlpatterns = patterns('',
    url(r'^$', views.ingest, name='ingest'),
    url(r'^upload$', views.upload, name="uploadEndpoint"),
    url(r'^blah$', views.blah, name="blah_del_me"),

#   RESTful end points
    url(r'^rest/', include(views.router.urls)),
)