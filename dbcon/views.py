from django.shortcuts import render, get_object_or_404
from django.views import generic

from datetime import date, datetime, time, timedelta

import mongoengine

from dbcon.models import *


def call_dates(first_date, second_date):
	'''For creating the dates and events in calendar'''
	def daterange(first_date, second_date):
		'''Calculation of the difference between the dates'''
		for n in range(int ((second_date - first_date).days)):
			yield first_date + timedelta(n)

	#Put the dates in a list as strings;
	datelist = []
	for single_date in daterange(first_date, second_date):
		datelist.append(single_date.strftime("%d-%m-20%y"))
	#This string format is important for passing the data with url
	#It is the 'dt' argument in the eventsofDate() method below.

	#Find the events of that dates and put them in a list
	eventObjlist = []
	for i in datelist:
		eventX = Events.objects(date=i)
		eventObjlist.append(eventX)

	#Combination of this lists helps to find the exact events of the exact date for calendar. 
	totallist1st = [{'datelist': t[0], 'eventObjlist': t[1]} for t in zip(datelist, eventObjlist)]
	return totallist1st


def calendar(request):
	if request.method == 'GET':
		#This is working, when you open the page for the first time.
		now_date = datetime.now()
		monthLater = now_date + timedelta(days=30)
	
		totallist = call_dates(now_date, monthLater)		
		
		#These are the texts when the page is opened for the first time;
		next30 = "Next 30 days from today;"
	
		return render(request, 'dbcon.html', {
				'totallist': totallist,
				'next30': next30,
			})

	elif request.method == 'POST':
		#This is working, if someone writes dates in input boxes.
		start_date = str(request.POST['start_date'])
		end_date = str(request.POST['end_date'])

		#Convert the strings to datetime;		
		startDate = datetime.strptime(start_date, '%d-%m-20%y')
		endDate = datetime.strptime(end_date, '%d-%m-20%y')

		totallist = call_dates(startDate, endDate)

		#These are the texts that apper when the dates chosen;
		dateRangetext = "The days between " + start_date + " and " + end_date + ";"

		return render(request, 'dbcon.html', {
				'totallist': totallist,
				'start_date': start_date,
				'end_date': end_date,
				'dateRangetext': dateRangetext,
			})


def eventsofDate(request, dt):
	'''Finds the events for the selected date. dt comes from the url.'''
	events_date_list = Events.objects(date=dt)
	return render(request, 'events.html', {
				'events_date_list': events_date_list,
				'eventDate': dt,
			})


def eventDetail(request, id):
	'''Finds the exact event via id.'''
	event = Events.objects.get(pk=id)
	return render(request, 'eventDetail.html', {
				'event': event,
			})















