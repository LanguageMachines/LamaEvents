from django.contrib import admin
admin.autodiscover()

from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from dbcon import views


urlpatterns = patterns('',

	#url(r'^admin/', include(admin.site.urls)),

	#url(r'^$', TemplateView.as_view(template_name="home.html")),

	url(r'^$', views.callendar), #include('dbcon.urls')), #Connected to dbcon directly

	url(r'^(?P<id>\w+)/tweets$', views.eventDetail),

	url(r'^(?P<dt>\S+|\S*[^\w\s]\S*)/events$', views.eventsofDate),

)
