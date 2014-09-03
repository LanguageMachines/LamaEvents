from django.conf.urls import patterns, include, url
#from django.views.generic import TemplateView

from dbcon import views

urlpatterns = patterns('',

	###url(r'^$', TemplateView.as_view(template_name="dbcon.html")),

	###url(r'^$', views.DbconView.as_view()),

	###url(r'^(?P<id>\w+)/tweets$', views.TweetsView.as_view()),	

	#url(r'^$', Calendar.as_view()),

	#url(r'^(?P<id>\w+)/eventDetail$', EventDetail.as_view()),

	#url(r'^(?P<dt>\S+|\S*[^\w\s]\S*)/events$', EventsofDate.as_view()),

	#url(r'^intervalseek/from:(?P<fst>\S+|\S*[^\w\s]\S*)to:(?P<snd>\S+|\S*[^\w\s]\S*)', IntervalSeek.as_view()),

	#All urls are working on LamaEvents/urls.py now.
	#If you want to use these again,
	#You have to add '/dbcon/' before the links in the all templates

)
