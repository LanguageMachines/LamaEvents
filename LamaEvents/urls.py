"""
This file makes the connections between views and the urls.

Some links pass informations to views. Example::

	# When a user click the link below in a template;
	<a href="/{{ event.linkDate }}/events"/>

	# This passes the 'dt' to EventsofDate view;
	url(r'^(?P<dt>\S+|\S*[^\w\s]\S*)/events$', EventsofDate.as_view()

	# Then you can use this 'dt' information in the view;
	class EventsofDate(View): 
		def get(self, request, dt):
			foo = dt...

.. warning:: The regular expressions in the url definitions must be suitable for the infi passed.

"""

#from django.contrib import admin
#admin.autodiscover()

from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from dbcon import views
from dbcon.views import *

urlpatterns = patterns('',

	#url(r'^admin/', include(admin.site.urls)),

	#url(r'^$', TemplateView.as_view(template_name="home.html")),

	url(r'^$', Calendar.as_view(), name="calendar"), #include('dbcon.urls')), #Connected to dbcon directly

	url(r'^intervalseek/from:(?P<fst>\S+|\S*[^\w\s]\S*)to:(?P<snd>\S+|\S*[^\w\s]\S*)', IntervalSeek.as_view()),

	url(r'^(?P<id>\w+)/eventDetail$', EventDetail.as_view()),

	url(r'^(?P<dt>\S+|\S*[^\w\s]\S*)/events$', EventsofDate.as_view()),

	url(r'^(?P<ov>\w+)-lama/$', About.as_view(), name="about"),

)
