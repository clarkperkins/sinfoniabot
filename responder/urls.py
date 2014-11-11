from django.conf.urls import patterns, url
from responder import views


urlpatterns = patterns(
    '',
    url(r'^bot/$', views.respond, name='bot'),
)
