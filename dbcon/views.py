from django.shortcuts import render, get_object_or_404
from django.views import generic

import mongoengine

from dbcon.models import *


class DbconView(generic.ListView):
	template_name = 'dbcon.html'
	context_object_name = 'latest_event_list'
	paginate_by = 5

	def get_queryset(self):
		return Events.objects.order_by('date')[:50] #'-' before 'id' is reversing the order

#def dbconview(request):
#	latest_event_list = Events.objects.order_by('date')[:50]	
#	return render(request, 'dbcon.html', {
#				'latest_event_list': latest_event_list,
#			})


#class TweetsView(generic.DetailView):
#	model = Events
#	template_name = 'tweets.html'


def eventDetail(request, id):
	event = Events.objects.get(pk=id)
	return render(request, 'tweets.html', {
				'event': event,
			})
