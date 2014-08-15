from django.conf.urls import patterns, include, url
#from django.views.generic import TemplateView

from dbcon import views

urlpatterns = patterns('',

	###url(r'^$', TemplateView.as_view(template_name="dbcon.html")),

	###url(r'^$', views.DbconView.as_view()),

	###url(r'^(?P<id>\w+)/tweets$', views.TweetsView.as_view()),	

	#url(r'^$', views.calendar),

	#url(r'^(?P<id>\w+)/tweets$', views.eventDetail),

	#url(r'^(?P<d>\S+|\S*[^\w\s]\S*)/events$', views.eventsofDate),

	# All urls are working on LamaEvents.urls now.
	#If you want to use these again,
	#You have to add '/dbcon/' before the links in templates

)
