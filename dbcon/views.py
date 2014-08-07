from django.shortcuts import render
from django.views import generic

import mongoengine

from dbcon.models import *


class DbconView(generic.ListView):
	template_name = 'dbcon.html'
	context_object_name = 'latest_event_list'
	paginate_by = 10

	def get_queryset(self):
		return Events.objects.order_by('-_id')[:50] #'-' before '_id' is reversing the order

class TweetsView(generic.DetailView):
	model = Events
	template_name = 'tweets.html'


