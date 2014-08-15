from django.shortcuts import render, get_object_or_404
from django.views import generic

from datetime import date, datetime, time, timedelta

import mongoengine

from dbcon.models import *


def calendar(request):

	now_date = datetime.now()
	monthLater = now_date + timedelta(days=30)

	def daterange(now_date, monthLater):
		for n in range(int ((monthLater - now_date).days)):
			yield now_date + timedelta(n)

	datelist = []
	for single_date in daterange(now_date, monthLater):
		datelist.append(single_date.strftime("%d-%m-20%y"))

	eventObjlist = []
	for i in datelist:
		eventX = Events.objects(date=i)
		eventObjlist.append(eventX)


	totallist = [{'datelist': t[0], 'eventObjlist': t[1]} for t in zip(datelist, eventObjlist)]

	return render(request, 'dbcon.html', {
				'totallist': totallist,
				'datelist': datelist,
				'eventObjlist': eventObjlist,
			})


def eventsofDate(request, dt):
	events_date_list = Events.objects(date=dt)
	return render(request, 'events.html', {
				'events_date_list': events_date_list,
				'dt': dt,
			})


def eventDetail(request, id):
	event = Events.objects.get(pk=id)
	return render(request, 'tweets.html', {
				'event': event,
			})















