from django.conf.urls import patterns, include, url
from django.contrib import admin
from web import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'packingcheck.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
)
