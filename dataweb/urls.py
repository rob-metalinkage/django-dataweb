from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()
from dataweb.views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dataweb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),
    url(r'manage/loadbase$', loadbase, name='loadbase'),
    url(r'manage/loadsamples$', loadsamples, name='loadsamples'),
    url(r'manage/flush$', flush_all, name='flush_all'),
)
