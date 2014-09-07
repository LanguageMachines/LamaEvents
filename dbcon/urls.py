"""

This file isn't in use. All urls are working on LamaEvents/urls.py and connected to views directly.

If you want to use this file again, replace the first code with the second code in LamaEvents/urls.py below::

	#Current code;
	url(r'^$', Calendar.as_view(), name="calendar")

	#Replace with;
	url(r'^$', include('dbcon.urls'))

Then activate these codes in dbcon/url.py::

	url(r'^$', Calendar.as_view(), name="calendar"),

	url(r'^intervalseek/from:(?P<fst>\S+|\S*[^\w\s]\S*)to:(?P<snd>\S+|\S*[^\w\s]\S*)', IntervalSeek.as_view()),

	url(r'^(?P<id>\w+)/eventDetail$', EventDetail.as_view()),

	url(r'^(?P<dt>\S+|\S*[^\w\s]\S*)/events$', EventsofDate.as_view()),

.. warning:: If you do this, it will add '/dbcon/' in front of the links. So you will have to add this to most of the links on templates

"""

from django.conf.urls import patterns, include, url
#from django.views.generic import TemplateView

from dbcon import views

urlpatterns = patterns('',

	#url(r'^$', Calendar.as_view(), name="calendar"),

	#url(r'^intervalseek/from:(?P<fst>\S+|\S*[^\w\s]\S*)to:(?P<snd>\S+|\S*[^\w\s]\S*)', IntervalSeek.as_view()),

	#url(r'^(?P<id>\w+)/eventDetail$', EventDetail.as_view()),

	#url(r'^(?P<dt>\S+|\S*[^\w\s]\S*)/events$', EventsofDate.as_view()),

)
