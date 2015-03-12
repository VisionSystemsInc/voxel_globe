from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.make_order_1, name='make_order_1'),)
