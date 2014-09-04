"""

'is_mobile' is for saying what will happen if the device is mobile. Works with basic if statement.

'urlprefix' is for the links to point on server.

'totallist = call_dates(x, y)' Calling the date-event calculator for the dates x and y and creating the totallist which we will use on the template. 

"""

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse

from datetime import datetime, timedelta

import mongoengine

from dbcon.models import *

from django.conf import settings

#!HINT! : To change the time interval in calendar change 'timeIntstr' (ex: week => "timeIntstr = 7")
timeIntstr_d = 6 #you can describe here 'how many dates will shown at start and during navigation'
time_interval_d = timeIntstr_d - 1 #'-1' is for making it look like time interval of twiqs.nl (For one day you have to write the same date twice, ex : 10-09-2014 & 10-09-2014)
#same thing for mobile version:
timeIntstr_m = 2
time_interval_m = timeIntstr_m - 1

#!IDEA! : you can ask the 'timeIntstr' value to user, for example with a dropdown menu.

#This format is used in strftimes and it is important for the links with dates. Links are passing this date format to make queries.
#if you change it, you will change the urls. Then you may be have to change the reqular expresion in the url.py too.
dateformat = "%d-%m-%Y"



def call_dates(first_date, second_date):
	"""
	For creating the dates and events in calendar and binding them to each others. 
	This is not a view! 
	It will create the calendar wherever it is needed.
	"""
	def daterange(first_date, second_date):
		"""Calculation of the difference between the dates"""
		for n in range((int((second_date - first_date).days))+1):
			yield first_date + timedelta(n)

	#Put the dates in lists with variations;
	datelist = []
	dateliststr = []
	datetimelist=[]
	for single_date in daterange(first_date, second_date):
		datelist.append(single_date.strftime(dateformat)) #These are for the link
		dateliststr.append(single_date.strftime("%d %b %Y %a")) #These are for showing
		datetimelist.append(datetime.strptime((single_date.strftime(dateformat)), dateformat)) #These are for query
		#Change this last code... Write a code to make the hour in datetimes 0.

	#!HINT! : To change how the dates are shown on the calendar, change strftime of 'dateliststr'.

	#Find the events of those dates and put them in a list;
	eventObjlist = []
	for i in datetimelist:
		eventX = Events.objects(date=i)
		eventObjlist.append(eventX)

	#Combination of this lists helps to find the events of the queried period for calendar.
	totallist1st = [{'datelist': t[0], 'dateliststr': t[1], 'eventObjlist': t[2], 'datetimelist': t[3]} for t in zip(datelist, dateliststr, eventObjlist, datetimelist)]
	return totallist1st


class Calendar(View):
	"""All the inputs on website are coming here to find results"""

	def get(self, request):
		"""
		This is working, when you open the page for the first time.
		It'll calculate the current date and add number of dates which you described with 'timeIntstr' at the beginning.
		"""
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
		
		#These are for the navigation with next or previous buttons;
		nextDate = dateLater.strftime(dateformat)
		nextnextDate = (dateLater + timedelta(days=time_interval)).strftime(dateformat)
		prevDate = (now_date + timedelta(days=-time_interval)).strftime(dateformat)
		currDate = now_date.strftime(dateformat)
	
		totallist = call_dates(now_date, dateLater) 

		return render(request, template, {
				'urlprefix': settings.URLPREFIX, #Calls the urlprefix from settings.
				'totallist': totallist,
				'nextDate': nextDate,
				'nextnextDate': nextnextDate,
				'prevDate': prevDate,
				'currDate': currDate,
				'timeIntstr' : timeIntstr,
		})



	def post(self, request):

		if "date_picker" in request.POST:
			"""This is working, if someone writes dates in input boxes."""
			#The input strings coming from input boxes. Also they are used for navigation with next or previous buttons;
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

			#Convert the strings to datetime for call_dates function;		
			startDate = datetime.strptime(start_date, dateformat)
			endDate = datetime.strptime(end_date, dateformat)

			#These are for the navigation links;
			nextnext3Date = (endDate + timedelta(days=time_interval)).strftime(dateformat)
			prev3Date = (startDate + timedelta(days=-time_interval)).strftime(dateformat)

			totallist = call_dates(startDate, endDate)

			return render(request, template, {
					'urlprefix': settings.URLPREFIX,
					'totallist': totallist,
					'start_date': start_date,
					'end_date': end_date,
					'nextnext3Date': nextnext3Date,
					'prev3Date': prev3Date,
			})



		elif "ttee" in request.POST:
			"""
			This is working, if someone writes hour and range in the second input box.
			It finds the events between these ranges. 
			For example hour=100 range=20, it'll show the events between 80(start_hour) and 120(end_hour) hour after from now.
			"""
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
				start_hour = datetime.now() #If search hour is smaller than the range, it'll set the start hour to now. So it can't show before now.

			end_hour = datetime.now() + timedelta(hours=(int(search_hour)+int(hour_range)))

			#These are for showing the date interval for the search;
			startHour = start_hour.strftime("%d %B %Y %H:00")
			endHour = end_hour.strftime("%d %B %Y %H:00")

			#Find events which fits 'end_hour > event.Estimation > start_hour'
			event_list = Events.objects(Q(Estimation__gte = start_hour) & Q(Estimation__lte = end_hour)).order_by('Estimation')

			return render(request, template, {
					'urlprefix': settings.URLPREFIX,
					'event_list': event_list,
					'startHour': startHour,
					'endHour': endHour,
			})



		elif "event_search" in request.POST:
			"""
			This is working, if someone writes keyterms in the search by keyterms input box.
			It'll find the events according to keyterms they wrote.
			fst_key: first keyterm, snd_key: second keyterm.
			"""
			fst_key = request.POST['fst_key']
			snd_key = request.POST['snd_key']

			if request.is_mobile:
				template = 'mobile/eventSearch.mobile.html'
			else:
				template = 'desktop/eventSearch.html'

			#Find events which have first or second keyterm and not in the past. 'iexact' means 'case insensitive';
			events_bykey_list = Events.objects(Q(Estimation__gte = datetime.now()) & (Q(keylist__iexact=fst_key) | Q(keylist__iexact=snd_key))).order_by('Estimation')

			return render(request, template, {
					'urlprefix': settings.URLPREFIX,
					'events_bykey_list': events_bykey_list,
					'fst_key': fst_key,
					'snd_key': snd_key,
			})



class IntervalSeek(View):
	"""
	If navigation links used, it will redirect the dates here and make a loop for dates.
	So if navigation link used again right after the first time, it will come here again.
	"""
	def get(self, request, fst, snd):
		"""fst: first day, snd: last day of the month. These parameters also used to create new navigation links."""

		if request.is_mobile:
			timeIntstr = timeIntstr_m
			time_interval = time_interval_m
			template = 'mobile/intervalseek.mobile.html'
		else:
			timeIntstr = timeIntstr_d
			time_interval = time_interval_d
			template = 'desktop/intervalseek.html'

		#These are for using the dates which come from links, in call_dates
		currDate2 = datetime.strptime(fst, dateformat)
		dateLater2 = currDate2 + timedelta(days=time_interval)

		#These are for the new navigation links.
		nextnext2Date = (dateLater2 + timedelta(days=time_interval)).strftime(dateformat)
		prev2Date = (currDate2 + timedelta(days=-time_interval)).strftime(dateformat)
	
		totallist = call_dates(currDate2, dateLater2)		

		return render(request, template, {
				'urlprefix': settings.URLPREFIX,
				'totallist': totallist,
				'fst': fst,
				'snd': snd,
				'nextnext2Date': nextnext2Date,
				'prev2Date': prev2Date,
		})



class EventsofDate(View):

	def get(self, request, dt):
		"""Finds the events for the selected date. dt comes from the url they click."""
		#Before making the query, change the string(dt) to datetime.
		events_date_list = Events.objects(date=datetime.strptime(dt, dateformat))
		
		#Calculates the next and previous days for the navigation links;
		nextDay = (datetime.strptime(dt, dateformat) + timedelta(days=1)).strftime(dateformat)
		prevDay = (datetime.strptime(dt, dateformat) + timedelta(days=-1)).strftime(dateformat)
	
		if request.is_mobile:
			template = 'mobile/events.mobile.html'
		else:
			template = 'desktop/events.html'

		return render(request, template, {
				'urlprefix': settings.URLPREFIX,
				'events_date_list': events_date_list,
				'eventDate': dt,
				'nextDay': nextDay,
				'prevDay': prevDay,
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
				'urlprefix': settings.URLPREFIX,
				'event': event,
		})


class About(View):

	def get(self, request):
		"""Redirects links to about pages."""

		if request.is_mobile:
			template = 'mobile/about.mobile.html'
		else:
			template = 'desktop/about.html'

		return render(request, template, {
			'urlprefix': settings.URLPREFIX,
		})



