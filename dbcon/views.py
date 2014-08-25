from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from django.core.paginator import Paginator

from datetime import datetime, timedelta

import mongoengine

from dbcon.models import *


#!!! All date searches are now monthly !!!
#If you want to search weekly; change all 'days=29' with 'days=6' (and 'days=-29' with 'days=-6') 


def call_dates(first_date, second_date):
	'''For creating the dates and events in calendar'''
	def daterange(first_date, second_date):
		'''Calculation of the difference between the dates'''
		for n in range((int((second_date - first_date).days))+1):
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


class Calendar(View):

	def get(self, request):
		#This is working, when you open the page for the first time.
		now_date = datetime.now()
		monthLater = now_date + timedelta(days=29)
		
		nextMonth = monthLater.strftime("%d-%m-20%y")
		nextnextMonth = (monthLater + timedelta(days=29)).strftime("%d-%m-20%y")
		prevMonth = (now_date + timedelta(days=-29)).strftime("%d-%m-20%y")
		currMonth = now_date.strftime("%d-%m-20%y")
	
		totallist = call_dates(now_date, monthLater)		
	
		return render(request, 'thismonth.html', {
				'totallist': totallist,
				'nextMonth': nextMonth,
				'nextnextMonth': nextnextMonth,
				'prevMonth': prevMonth,
				'currMonth': currMonth,
		})



	def post(self, request):

		if "date_picker" in request.POST:
			#This is working, if someone writes dates in input boxes.
			start_date = request.POST['start_date']
			end_date = request.POST['end_date']

			#Convert the strings to datetime;		
			startDate = datetime.strptime(start_date, '%d-%m-20%y')
			endDate = datetime.strptime(end_date, '%d-%m-20%y')

			nextnext3Month = (endDate + timedelta(days=29)).strftime("%d-%m-20%y")
			prev3Month = (startDate + timedelta(days=-29)).strftime("%d-%m-20%y")

			totallist = call_dates(startDate, endDate)


			return render(request, 'datepicker.html', {
					'totallist': totallist,
					'start_date': start_date,
					'end_date': end_date,
					'nextnext3Month': nextnext3Month,
					'prev3Month': prev3Month,
			})



		elif "ttee" in request.POST:
			#This is working, if someone writes hour and range in input box.
			search_hour = request.POST['search_hour']
			hour_range = request.POST['hour_range']

			#For not to see the events in the past;
			if int(search_hour) > int(hour_range):
				start_hour = datetime.now() + timedelta(hours=(int(search_hour)-int(hour_range)))
			else:
				start_hour = datetime.now()

			end_hour = datetime.now() + timedelta(hours=(int(search_hour)+int(hour_range)))

			startHour = start_hour.strftime("%d %B 20%y %H:00")
			endHour = end_hour.strftime("%d %B 20%y %H:00")

			#Find events which fits 'end_hour > event.Estimation > start_hour'
			event_list = Events.objects(Q(Estimation__gte = start_hour) & Q(Estimation__lte = end_hour)).order_by('Estimation')

			return render(request, 'ttee.html', {
					'event_list': event_list, 
					'startHour': startHour,
					'endHour': endHour,
			})


		elif "event_search" in request.POST:
			#This is working, if someone writes keyterms in the search by keyterms input box.
			fst_key = request.POST['fst_key']
			snd_key = request.POST['snd_key']

			#Find events which have first or second keyterm. iexact = case insensitive.
			events_bykey_list = Events.objects(Q(keylist__iexact=fst_key) | Q(keylist__iexact=snd_key))

			return render(request, 'eventSearch.html', {
					'events_bykey_list': events_bykey_list,
					'fst_key': fst_key,
					'snd_key': snd_key,
			})



class MonthSeek(View):

	def get(self, request, fst, snd):
		'''fst: first day, snd: last day of the month'''
		currMonth2 = datetime.strptime(fst, '%d-%m-20%y')
		monthLater2 = currMonth2 + timedelta(days=29)

		nextnext2Month = (monthLater2 + timedelta(days=29)).strftime("%d-%m-20%y")
		prev2Month = (currMonth2 + timedelta(days=-29)).strftime("%d-%m-20%y")
	
		totallist = call_dates(currMonth2, monthLater2)		

		return render(request, 'monthseek.html', {
				'totallist': totallist,
				'fst': fst,
				'snd': snd, 
				'nextnext2Month': nextnext2Month,
				'prev2Month': prev2Month,
		})



class EventsofDate(View):

	def get(self, request, dt):
		'''Finds the events for the selected date. dt comes from the url.'''
		events_date_list = Events.objects(date=dt)
		
		nextDay = (datetime.strptime(dt, '%d-%m-20%y') + timedelta(days=1)).strftime("%d-%m-20%y")
		prevDay = (datetime.strptime(dt, '%d-%m-20%y') + timedelta(days=-1)).strftime("%d-%m-20%y")

		
		return render(request, 'events.html', {
				'events_date_list': events_date_list,
				'eventDate': dt,
				'nextDay': nextDay,
				'prevDay': prevDay,
		})


class EventDetail(View):

	def get(self, request, id):
		'''Finds the exact event via id.'''
		event = Events.objects.get(pk=id)
		return render(request, 'eventDetail.html', {
				'event': event,
		})




