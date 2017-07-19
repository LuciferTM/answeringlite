from django.conf.urls import patterns, include, url
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

def gikoo_url(regex, view, kwargs=None, name=None, prefix=''):
    url_prefix = '^' + settings.GIKOO['api_url_prefix'][1:]
    regex = url_prefix + regex
    return url(regex, view, kwargs, name, prefix)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'answeringlite.views.home', name='home'),
    # url(r'^answeringlite/', include('answeringlite.foo.urls')),

    # # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    #
    # # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    gikoo_url(r'wechat/', include('wechat.urls')),
)
