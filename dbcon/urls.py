from django.conf.urls import patterns, include, url
#from django.views.generic import TemplateView

from dbcon import views

urlpatterns = patterns('',

	#url(r'^$', TemplateView.as_view(template_name="dbcon.html"), name='dbcon'),

	url(r'^$', views.DbconView.as_view(), name='dbcon'),
	
	#url(r'^$', views.dbconview, name='tweets'),

	#url(r'^(?P<id>\w+)/tweets$', views.TweetsView.as_view(), name='tweets'),

	url(r'^(?P<id>\w+)/tweets$', views.eventDetail, name='tweets'),

)
