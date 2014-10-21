from django.conf.urls import patterns, include, url

from django.contrib import admin

#handler400 = 'world.views.error400page'
#AEN: THIS doesn't work!

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'nga.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^world/', include('world.urls', namespace='world')),
    url(r'^$', include('meta.urls', namespace='meta')),
    url(r'^meta/rest/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^meta/', include('meta.urls', namespace='meta')),
)
