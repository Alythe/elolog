from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views
from registration.views import activate
from registration.views import register

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'log.views.index'),
    
    url(r'^logs/$', 'log.views.logs', name="my_logs"),
    url(r'^public/$', 'log.views.logs', {'public': True}, name="public_logs"),
    
    url(r'^logs/(?P<log_id>\d+)/$', 'log.views.view'),
    url(r'^logs/(?P<log_id>\d+)/publish/$', 'log.views.publish'),
    url(r'^logs/(?P<log_id>\d+)/unpublish/$', 'log.views.unpublish'),
    url(r'^logs/(?P<log_id>\d+)/edit/$', 'log.views.edit_log'),
    url(r'^logs/(?P<log_id>\d+)/delete/$', 'log.views.delete_log'),
    
    url(r'^public/(?P<log_id>[a-fA-F\d]{10})/$', 'log.views.view', {'public': True}),
    url(r'^public/(?P<log_id>[a-fA-F\d]{10})/graph$', 'log.views.graph_log', {'public': True}),

    url(r'^logs/(?P<log_id>\d+)/edit/(?P<item_id>\d+)/$', 'log.views.edit_item'),
    url(r'^logs/(?P<log_id>\d+)/delete/(?P<item_id>\d+)/$', 'log.views.delete_item'),
    url(r'^logs/(?P<log_id>\d+)/new/$', 'log.views.edit_item'),
    url(r'^logs/(?P<log_id>\d+)/export/$', 'log.views.export_log'),
    url(r'^logs/(?P<log_id>\d+)/graph/$', 'log.views.graph_log'),
    url(r'^new/$', 'log.views.edit_log'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^resend_activation/', 'log.views.resend_activation'),
    #url(r'^signup/$', 'log.views.signup'),
    url(r'^about/$', direct_to_template, {'template': 'about.html'}, name="about"),
    url(r'^news/$', 'log.views.news'),
    url(r'^news/(?P<news_id>\d+)/$', 'log.views.news_comments'),
    url(r'^stats/$', 'log.views.global_stats'),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #(r'^forum/', include('djangobb_forum.urls', namespace='djangobb')),
)

urlpatterns += patterns('',
    url(r'^activate/complete/$',
        direct_to_template,
        { 'template': 'registration/activation_complete.html' },
        name='registration_activation_complete'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$',
        activate,
        { 'backend': 'log.registration_backend.LogRegistrationBackend' },
        name='registration_activate'),
    url(r'^register/$',
        register,
        { 'backend': 'log.registration_backend.LogRegistrationBackend' },
        name='registration_register'),
    url(r'^register/complete/$',
        direct_to_template,
        { 'template': 'registration/registration_complete.html' },
        name='registration_complete'),
    url(r'^register/closed/$',
        direct_to_template,
        { 'template': 'registration/registration_closed.html' },
        name='registration_disallowed'),
    (r'', include('registration.auth_urls')),
)
