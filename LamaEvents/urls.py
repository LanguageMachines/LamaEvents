from django.contrib import admin
admin.autodiscover()

from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from dbcon import views
from dbcon.views import *

urlpatterns = patterns('',

	#url(r'^admin/', include(admin.site.urls)),

	#url(r'^$', TemplateView.as_view(template_name="home.html")),

	url(r'^$', Calendar.as_view()), #include('dbcon.urls')), #Connected to dbcon directly

	url(r'^intervalseek/from:(?P<fst>\S+|\S*[^\w\s]\S*)to:(?P<snd>\S+|\S*[^\w\s]\S*)', IntervalSeek.as_view()),

	url(r'^(?P<id>\w+)/eventDetail$', EventDetail.as_view()),

	url(r'^(?P<dt>\S+|\S*[^\w\s]\S*)/events$', EventsofDate.as_view()),

)
