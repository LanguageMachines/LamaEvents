"""
Hey there

.. module:: dbcon.views
   :platform: Linux
   :synopsis: A useful module indeed.


"""

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse

from datetime import datetime, timedelta

import mongoengine

from dbcon.models import *

from django.conf import settings

#!HINT! : To change the time interval in calendar change 'timeIntstr' (ex: week => "timeIntstr = 7")
timeIntstr_d = 3
time_interval_d = timeIntstr_d - 1 #to show it on template (nextint.html)
#sate thing for mobile version:
timeIntstr_m = 2
time_interval_m = timeIntstr_m - 1

#!IDEA! : you can ask the 'timeIntstr' value to user, for example with a dropdown menu.


def call_dates(first_date, second_date):
	"""For creating the dates and events in calendar"""
	def daterange(first_date, second_date):
		"""Calculation of the difference between the dates"""
		for n in range((int((second_date - first_date).days))+1):
			yield first_date + timedelta(n)

	#Put the dates in lists as strings;
	datelist = []
	dateliststr = []
	for single_date in daterange(first_date, second_date):
		datelist.append(single_date.strftime("%d-%m-%Y"))
		dateliststr.append(single_date.strftime("%d %b %Y %a"))
	#!INFO! : "datelist" string format is important for passing the data with url and finding the events. It is the 'dt' argument in the EventsofDate view below.
	#!HINT! : To change how the dates are shown on the calendar change it's strftime. (ex: 30 Aug 2014 Sat = "%d %b %Y %a")

	#Find the events of that dates and put them in a list;
	eventObjlist = []
	for i in datelist:
		eventX = Events.objects(date=i)
		eventObjlist.append(eventX)

	#Combination of this lists helps to find the exact events of the exact date for calendar.
	totallist1st = [{'datelist': t[0], 'dateliststr': t[1], 'eventObjlist': t[2]} for t in zip(datelist, dateliststr, eventObjlist)]
	return totallist1st


class Calendar(View):

	def get(self, request):
		"""This is working, when you open the page for the first time."""
		if request.is_mobile:
			timeIntstr = timeIntstr_m
			time_interval = time_interval_m
			template = 'mobile/nextint.mobile.html'
		else:
			timeIntstr = timeIntstr_d
			time_interval = time_interval_d
			template = 'desktop/nextint.html'

		now_date = datetime.now()
		dateLater = now_date + timedelta(days=time_interval)
		
		nextDate = dateLater.strftime("%d-%m-%Y")
		nextnextDate = (dateLater + timedelta(days=time_interval)).strftime("%d-%m-%Y")
		prevDate = (now_date + timedelta(days=-time_interval)).strftime("%d-%m-%Y")
		currDate = now_date.strftime("%d-%m-%Y")
	
		totallist = call_dates(now_date, dateLater)		

		return render(request, template, {
				'totallist': totallist,
				'nextDate': nextDate,
				'nextnextDate': nextnextDate,
				'prevDate': prevDate,
				'currDate': currDate,
				'timeIntstr' : timeIntstr,
				'urlprefix': settings.URLPREFIX,
		})



	def post(self, request):

		if "date_picker" in request.POST:
			#This is working, if someone writes dates in input boxes.
			start_date = request.POST['start_date']
			end_date = request.POST['end_date']

			if request.is_mobile:
				timeIntstr = timeIntstr_m
				time_interval = time_interval_m
				template = 'mobile/datepicker.mobile.html'
			else:
				timeIntstr = timeIntstr_d
				time_interval = time_interval_d
				template = 'desktop/datepicker.html'

			#Convert the strings to datetime;		
			startDate = datetime.strptime(start_date, '%d-%m-%Y')
			endDate = datetime.strptime(end_date, '%d-%m-%Y')


			nextnext3Date = (endDate + timedelta(days=time_interval)).strftime("%d-%m-%Y")
			prev3Date = (startDate + timedelta(days=-time_interval)).strftime("%d-%m-%Y")

			totallist = call_dates(startDate, endDate)

			return render(request, template, {
					'totallist': totallist,
					'start_date': start_date,
					'end_date': end_date,
					'nextnext3Date': nextnext3Date,
					'prev3Date': prev3Date,
					'urlprefix': settings.URLPREFIX,
			})



		elif "ttee" in request.POST:
			#This is working, if someone writes hour and range in input box.
			search_hour = request.POST['search_hour']
			hour_range = request.POST['hour_range']

			if request.is_mobile:
				template = 'mobile/ttee.mobile.html'
			else:
				template = 'desktop/ttee.html'

			#For not to see the events in the past;
			if int(search_hour) > int(hour_range):
				start_hour = datetime.now() + timedelta(hours=(int(search_hour)-int(hour_range)))
			else:
				start_hour = datetime.now()

			end_hour = datetime.now() + timedelta(hours=(int(search_hour)+int(hour_range)))

			startHour = start_hour.strftime("%d %B %Y %H:00")
			endHour = end_hour.strftime("%d %B %Y %H:00")

			#Find events which fits 'end_hour > event.Estimation > start_hour'
			event_list = Events.objects(Q(Estimation__gte = start_hour) & Q(Estimation__lte = end_hour)).order_by('Estimation')

			return render(request, template, {
					'event_list': event_list,
					'startHour': startHour,
					'endHour': endHour,
					'urlprefix': settings.URLPREFIX,
			})



		elif "event_search" in request.POST:
			#This is working, if someone writes keyterms in the search by keyterms input box.
			fst_key = request.POST['fst_key']
			snd_key = request.POST['snd_key']

			if request.is_mobile:
				template = 'mobile/eventSearch.mobile.html'
			else:
				template = 'desktop/eventSearch.html'

			#Find events which have first or second keyterm and not in the past. iexact = case insensitive.
			events_bykey_list = Events.objects(Q(Estimation__gte = datetime.now()) & (Q(keylist__iexact=fst_key) | Q(keylist__iexact=snd_key))).order_by('Estimation')

			return render(request, template, {
					'events_bykey_list': events_bykey_list,
					'fst_key': fst_key,
					'snd_key': snd_key,
					'urlprefix': settings.URLPREFIX,
			})



class IntervalSeek(View):
	"""fst: first day, snd: last day of the month"""
	def get(self, request, fst, snd):
		"""fst: first day, snd: last day of the month"""

		if request.is_mobile:
			timeIntstr = timeIntstr_m
			time_interval = time_interval_m
			template = 'mobile/intervalseek.mobile.html'
		else:
			timeIntstr = timeIntstr_d
			time_interval = time_interval_d
			template = 'desktop/intervalseek.html'

		currDate2 = datetime.strptime(fst, '%d-%m-%Y')
		dateLater2 = currDate2 + timedelta(days=time_interval)


		nextnext2Date = (dateLater2 + timedelta(days=time_interval)).strftime("%d-%m-%Y")
		prev2Date = (currDate2 + timedelta(days=-time_interval)).strftime("%d-%m-%Y")
	
		totallist = call_dates(currDate2, dateLater2)		


		return render(request, template, {
				'totallist': totallist,
				'fst': fst,
				'snd': snd,
				'nextnext2Date': nextnext2Date,
				'prev2Date': prev2Date,
				'urlprefix': settings.URLPREFIX,
		})



class EventsofDate(View):

	def get(self, request, dt):
		"""Finds the events for the selected date. dt comes from the url."""
		events_date_list = Events.objects(date=dt)
		
		nextDay = (datetime.strptime(dt, '%d-%m-%Y') + timedelta(days=1)).strftime("%d-%m-%Y")
		prevDay = (datetime.strptime(dt, '%d-%m-%Y') + timedelta(days=-1)).strftime("%d-%m-%Y")
	
		if request.is_mobile:
			template = 'mobile/events.mobile.html'
		else:
			template = 'desktop/events.html'

		return render(request, template, {
				'events_date_list': events_date_list,
				'eventDate': dt,
				'nextDay': nextDay,
				'prevDay': prevDay,
				'urlprefix': settings.URLPREFIX,
		})


class EventDetail(View):

	def get(self, request, id):
		"""Finds the exact event via id."""
		event = Events.objects.get(pk=id)

		if request.is_mobile:
			template = 'mobile/eventDetail.mobile.html'
		else:
			template = 'desktop/eventDetail.html'

		return render(request, template, {
				'event': event,
				'urlprefix': settings.URLPREFIX,
		})


class About(View):

	def get(self, request):
		"""About Pages"""

		if request.is_mobile:
			template = 'mobile/about.mobile.html'
		else:
			template = 'desktop/about.html'

		return render(request, template, {
			'urlprefix': settings.URLPREFIX,
		})



