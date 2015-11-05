"""
This is the standart views file for Django.  


.. rubric:: Some Explanations

With using 'timeIntstr_d' and 'timeIntstr_m' you can describe here how many dates will shown at 
start and during navigation on calendar. '-1' is for making it look like time interval of 
twiqs.nl (For one day you have to write the same date twice, ex : 10-09-2014 & 10-09-2014).
'_d' stands for 'desktop' and '_m' stands for 'mobile'::

	#Desktop;
	timeIntstr_d = 6 
	time_interval_d = timeIntstr_d - 1
	#Mobile;
	timeIntstr_m = 2
	time_interval_m = timeIntstr_m - 1
	

'is_mobile' is for saying what will happen if the device is mobile. Works with basic if statement. Also see LamaEvents/middleware.py::

		if request.is_mobile:
			timeIntstr = timeIntstr_m
			time_interval = time_interval_m
			template = 'mobile/nextint.mobile.html'
		else:
			timeIntstr = timeIntstr_d
			time_interval = time_interval_d
			template = 'desktop/nextint.html'

The following code is used in many strftime & strptime convertions. It is important for the links with dates 
because links are passing this date format to make queries. Therefore if you change it, you will change the urls. 
Then you may be have to change the reqular expresion in the url.py too::

	dateformat = "%d-%m-%Y"


On the Applejack server, the link starts with '/lamaevents'. Because of that we defined a variable called urlprefix in settings.py.
And here we are sending this variable to templates for adding to the links::

		return render(request, template, {
			'urlprefix': settings.URLPREFIX,




:Contents:
"""

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse

from datetime import datetime, timedelta

import locale

import mongoengine

from dbcon.models import * #Event and Tweet models

from django.conf import settings


timeIntstr_d = 6 
time_interval_d = timeIntstr_d - 1 

timeIntstr_m = 2
time_interval_m = timeIntstr_m - 1


dateformat = "%d-%m-%Y"


#To implement Dutch dates (E.g. Dinsdag 12 mei 2015);
locale.setlocale(locale.LC_TIME, "nl_NL.utf8")



def call_dates(first_date, second_date):
	"""
	For creating the dates and events in calendar and binding them to each others. 
	This is not a view! 

	:param first_date: The Start Date
	:param second_date: The End Date	

	First it calculates the all dates between the start date and the end date. Then put them in 4 different lists as different values and zip them in one list;
	
		1. datelist = Used in the links to show events for one date. Resulted in dateitem.
		2. dateliststr = Used to show dates as strings in format "%d %b %Y %a" (e.g.: 09 Sep 2014 Tue). Resulted in dateitemstr.
		3. datetimelist = Used to query events. Items are in datetime format. Resulted in datetimeitem.
		4. eventObjlist = Holds the events found by querying with items in datetimelist. Resulted in eventObj.

	.. rubric::	Usage of call_dates()

	In the views which we will use calendar there must be two exact dates. 
	We need to call call_dates() method with using this dates as parameters and assign to a list::
 
		allperEventsDictList = call_dates(now_date, dateLater) 

		#And we have to render this to template;
		return render(request, template, {
			'allperEventsDictList': allperEventsDictList,

	Then you can call them is template like this::

		#Iterate on the allperEventsDictList. each element of allperEventsDictList is a dictionary whose keys identify dateitem, dateitemstr, eventObj, datetimeitem;
		{% for x in allperEventsDictList %}

			#eventObj is a list of events of a date. Thus, event is a Events class instance;
			{% for event in x.eventObj %}
					{{ event.score }}

	"""

	def daterange(first_date, second_date):
		"""Calculation of the difference between the dates"""
		for n in range((int((second_date - first_date).days))+1):
			yield first_date + timedelta(n)

	datelist = []
	dateliststr = []
	datetimelist=[]
	for single_date in daterange(first_date, second_date):
		datelist.append(single_date.strftime(dateformat)) 
		dateliststr.append(single_date.strftime("%A %d %b %Y").title())
		datetimelist.append(datetime.strptime((single_date.strftime(dateformat)), dateformat)) 
		#Change this last code... Write a code to make the hour in datetimes 0.

	#!HINT! : To change how the dates are shown on the calendar, change strftime of 'dateliststr'.

	#Find the events of those dates and put them in a list;
	eventObjlist = []
	for i in datetimelist:
		eventX = Events.objects(date=i).order_by('-score')
		eventObjlist.append(eventX)

	#Combination of this lists helps to find the events of the queried period for calendar.
	allperEventsDictList1st = [{'dateitem': t[0], 'dateitemstr': t[1], 'eventObj': t[2], 'datetimeitem': t[3]} for t in zip(datelist, dateliststr, eventObjlist, datetimelist)]
	return allperEventsDictList1st


class Calendar(View):
	"""All the inputs on website are coming here to find results"""

	def get(self, request):
		"""
		Calculates the current date and add number of dates which you described with 'timeIntstr' at the beginning. 
		This is working, when you open the main page for the first time.
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
	
		allperEventsDictList = call_dates(now_date, dateLater) 

		return render(request, template, {
				'urlprefix': settings.URLPREFIX, #Calls the urlprefix from settings.
				'allperEventsDictList': allperEventsDictList,
				'nextDate': nextDate,
				'nextnextDate': nextnextDate,
				'prevDate': prevDate,
				'currDate': currDate,
				'timeIntstr' : timeIntstr,
		})



	def post(self, request):
		"""
		post() is used for user inputs. 

		There are if statements inside to find out which button submitted;

		1. Date Picker;

			* This is working, if someone used 'Specificeer Datums' search.
			* Assign the parameters to new string variables. These are also used for navigation with next or previous buttons::

				start_date = request.POST['start_date']
				end_date = request.POST['end_date']	

			* Convert the strings to datetime for call_dates function::

				startDate = datetime.strptime(start_date, dateformat)
				endDate = datetime.strptime(end_date, dateformat)
			
				allperEventsDictList = call_dates(startDate, endDate)

		:param start_date:
		:param end_date:


		2. Time-To-Event Estimation;

			* This is working, if someone used "Specificeer Uren" search.
			* It finds the events between these ranges. For example hour=100 range=20, it'll show the events between 80(start_hour) and 120(end_hour) hour after from now.
			* If search hour is smaller than the range, it'll set the start hour to now. So it can't show before now::

				if int(search_hour) > int(hour_range): 
					start_hour = datetime.now() + timedelta(hours=(int(search_hour)-int(hour_range)))
				else:
					start_hour = datetime.now() 

			* Find events which fits 'end_hour > event.Estimation > start_hour'::

				event_list = Events.objects(Q(Estimation__gte = start_hour) & Q(Estimation__lte = end_hour)).order_by('Estimation')

		:param search_hour:
		:param hour_range: 


		3. Event Search;
	
			* This is working, if someone used "Zoek met Zoekwoorden" search.

			* It'll find the events according to keyterms they wrote. 

			* The query finds events which have first or second keyterm and not in the past. 'iexact' means 'case insensitive'::

				event_list = Events.objects()
#				event_list = Events.objects(Q(Estimation__gte = start_hour) & Q(Estimation__lte = end_hour)).order_by('Estimation')


		:param fst_key: First Keyterm
		:param snd_key: Second Keyterm

		"""

		if "date_picker" in request.POST:

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

				
			startDate = datetime.strptime(start_date, dateformat)
			endDate = datetime.strptime(end_date, dateformat)

			#These are for the navigation links;
			nextnext3Date = (endDate + timedelta(days=time_interval)).strftime(dateformat)
			prev3Date = (startDate + timedelta(days=-time_interval)).strftime(dateformat)

			allperEventsDictList = call_dates(startDate, endDate)

			return render(request, template, {
					'urlprefix': settings.URLPREFIX,
					'allperEventsDictList': allperEventsDictList,
					'start_date': start_date,
					'end_date': end_date,
					'nextnext3Date': nextnext3Date,
					'prev3Date': prev3Date,
			})



		elif "ttee" in request.POST:

			search_hour = request.POST['search_hour']
			hour_range = request.POST['hour_range']

			if request.is_mobile:
				template = 'mobile/ttee.mobile.html'
			else:
				template = 'desktop/ttee.html'

			if int(search_hour) > int(hour_range): 
				start_hour = datetime.now() + timedelta(hours=(int(search_hour)-int(hour_range)))
			else:
				start_hour = datetime.now() 

			end_hour = datetime.now() + timedelta(hours=(int(search_hour)+int(hour_range)))

			#These are for showing the date interval for the search;
			startHour = start_hour.strftime("%d %B %Y %H:00")
			endHour = end_hour.strftime("%d %B %Y %H:00")

			event_list = Events.objects(Q(date__gte = start_hour) & Q(date__lte = end_hour)).order_by('date')

			return render(request, template, {
					'urlprefix': settings.URLPREFIX,
					'event_list': event_list,
					'startHour': startHour,
					'endHour': endHour,
			})



		elif "event_search" in request.POST:

			fst_key = request.POST['fst_key']
			snd_key = request.POST['snd_key']

			if request.is_mobile:
				template = 'mobile/eventSearch.mobile.html'
			else:
				template = 'desktop/eventSearch.html'

			#events_bykey_list = Events.objects(Q(Estimation__gte = datetime.now()) & (Q(keylist__iexact=fst_key) | Q(keylist__iexact=snd_key))).order_by('Estimation')
			events_bykey_list = Events.objects((Q(keylist__iexact=fst_key) | Q(keylist__iexact=snd_key)))

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

	This is using call_dates() with the new dates coming from the links.

	The date amount to show is defined with 'timeIntstr' again.
	"""
	def get(self, request, fst, snd):
		"""
		:param fst: First Day
		:param snd: Last Day

		These parameters also used to create new navigation links.
		"""
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
	
		allperEventsDictList = call_dates(currDate2, dateLater2)		

		return render(request, template, {
				'urlprefix': settings.URLPREFIX,
				'allperEventsDictList': allperEventsDictList,
				'fst': fst,
				'snd': snd,
				'nextnext2Date': nextnext2Date,
				'prev2Date': prev2Date,
		})



class EventsofDate(View):
	"""This view shows the events for a specific date"""

	def get(self, request, dt):
		"""
		Finds the events for the selected date. dt comes from the url which is clicked.

		Before making the query, change the string(dt) to datetime::

			events_date_list = Events.objects(date=datetime.strptime(dt, dateformat)).order_by('-score')

		:param dt: Comes from the links

		"""
		events_date_list = Events.objects(date=datetime.strptime(dt, dateformat)).order_by('-score')
		
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
	"""This view shows the details of the events such as tweets about it"""

	def get(self, request, id):
		"""
		Finds the exact event via id.

		:param id: Comes from the links

		"""
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
	"""Redirects links to about pages."""
	def get(self, request, ov):

		if request.is_mobile:
			template = 'mobile/'+ ov +'-lama.mobile.html'
		else:
			template = 'desktop/'+ ov +'-lama.html'

		return render(request, template, {
			'urlprefix': settings.URLPREFIX,
		})



