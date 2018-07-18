"""
This file makes the connections between views and the urls.

Some links pass informations to views. Example::

	# When a user click the link below in a template;
	<a href="/{{ event.linkDate }}/events"/>

	# This passes the 'dt' to EventsofDate view;
	path(r'^(?P<dt>\S+|\S*[^\w\s]\S*)/events$', EventsofDate.as_view()

	# Then you can use this 'dt' information in the view;
	class EventsofDate(View): 
		def get(self, request, dt):
			foo = dt...

.. warning:: The regular expressions in the url definitions must be suitable for the infi passed.

"""
#from django.views.generic import TemplateView
from django.urls import path, re_path
from django.conf.urls import handler404, handler500

from dbcon import views
from dbcon.views import *

urlpatterns = [

	#path(r'^admin/', include(admin.site.urls)),

	#path(r'^$', TemplateView.as_view(template_name="home.html")),

	re_path(r'^$', Calendar.as_view(), name="calendar"), #include('dbcon.urls')), #Connected to dbcon directly

	re_path(r'^intervalseek/from:(?P<fst>\S+|\S*[^\w\s]\S*)to:(?P<snd>\S+|\S*[^\w\s]\S*)', IntervalSeek.as_view()),

	re_path(r'^(?P<id>\w+)/eventDetail$', EventDetail.as_view()),

	re_path(r'^(?P<dt>\S+|\S*[^\w\s]\S*)/events$', EventsofDate.as_view()),

	re_path(r'^(?P<ov>\w+)-lama/$', About.as_view()),

        re_path(r'^inf$', NonInfo.as_view()),
                     
	re_path(r'^404$', Error404.as_view(), name="Error404"),
	re_path(r'^500$', Error500.as_view(), name="Error500"),

]

handler404 = views.custom_handler_404
handler500 = views.custom_handler_500

