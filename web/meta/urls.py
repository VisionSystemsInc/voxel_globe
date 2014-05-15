from django.conf.urls import patterns, url

from meta import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)