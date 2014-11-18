from django.conf.urls import patterns, url, include
import views

urlpatterns = patterns('',
    url(r'^$', views.make_order, name='make_order'),
    url(r'^order/(?P<image_collection_id>\d+)/$', views.order, name="order"),
)