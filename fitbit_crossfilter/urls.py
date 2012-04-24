from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'foo.views.index'),
    url(r'^login$', 'foo.views.login'),
    url(r'^oauth$', 'foo.views.oauth')
)
