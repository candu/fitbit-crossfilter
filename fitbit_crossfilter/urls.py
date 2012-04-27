from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'foo.views.index'),
    url(r'^login$', 'foo.views.login'),
    url(r'^logout$', 'foo.views.logout'),
    url(r'^sync-user-data$', 'foo.views.sync_user_data'),
    url(r'^get-user-data$', 'foo.views.get_user_data'),
    url(r'^oauth$', 'foo.views.oauth')
)
