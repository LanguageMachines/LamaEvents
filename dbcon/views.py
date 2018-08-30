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
====================== Error 402 ========================
'django.contrib.auth.context_processors.auth'
 must be in TEMPLATES in order to use the admin application.
=========================================================
"""

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse

from datetime import datetime, timedelta

import locale

from bson import ObjectId

from django.conf import settings

timeIntstr_d = 6 
time_interval_d = timeIntstr_d - 1 

timeIntstr_m = 2
time_interval_m = timeIntstr_m - 1

dateformat = "%d-%m-%Y"

setDateToSearchs = False
dateSearchOk = False

#To implement Dutch dates (E.g. Dinsdag 12 mei 2015);
locale.setlocale(locale.LC_TIME, "nl_NL.utf8")

def enrich_events(event_list):

        # check if event_list is a pymongo.cursor.Cursor object and run the next line
        event_list = [e for e in event_list]
        
        event_type_dict_nDut = {'public event': 'Evenement', 'sport': 'Sport', 'social action': 'Sociale actie', 'politics': 'Politiek', 'software': 'Software', 'special day': 'Speciale dag', 'advertisement': 'Advertentie', 'broadcast': 'Uitzending', 'other' : 'Anders'}

        event_type_dict_nEng = {'Evenement':'public event', 'Sport': 'sport', 'Sociale actie': 'social action', 'Politiek': 'politics', 'Software': 'software', 'Speciale dag': 'special day', 'Advertentie':'advertisement', 'Uitzending': 'broadcast', 'Anders': 'other'}

        for event in event_list:
                event['id'] = str(event['_id'])
                event['linkDate'] = event['date'].strftime("%d-%m-%Y")
                event['datestr1'] = event['date'].strftime("%A").title()
                event['datestr2'] = event['date'].strftime("%d %B %Y")
                event['datestr3'] = event['date'].strftime("%H.%M uur")
                event['datestr4'] = event['date'].strftime("%Y-%m-%d")
                event['entities_str'] = ', '.join(event['entities'])

                if event['eventtype']:
                        event['type_nDut'] = event_type_dict_nDut[event['eventtype']]
                else:
                        event['type_nDut'] = 'Anders'
                event['entities_str'] = ', '.join(event['entities'])

#                print(event)
        return event_list

def call_dates(first_date, second_date, periodic_filter, fst_key=None, snd_key=None, evenementen=[], lst_qty=0):

        def daterange(first_date, second_date):
                """Calculation of the difference between the dates"""
                for n in range((int((second_date - first_date).days))+1):
                        yield first_date + timedelta(n)

        datelist = []
        dateliststr = []
        datetimelist = []
        foundEventsForDates = False
        for single_date in daterange(first_date, second_date):
                datelist.append(single_date.strftime(dateformat)) ## Is it necessary to  
                dateliststr.append(single_date.strftime("%A %d %b %Y").title())
                datetimelist.append(datetime.strptime((single_date.strftime(dateformat)), dateformat)) 
                #Change this last code... Write a code to make the hour in datetimes 0.

        #!HINT! : To change how the dates are shown on the calendar, change strftime of 'dateliststr'.

        #Find the events of those dates and put them in a list;
        eventObjlist = []

        for event_date in datetimelist:
                if fst_key and lst_qty > 0: 
                        eventX = settings.LAMAEVENT_COLL.find({'date' : event_date, '$or': [{'entities': fst_key}, {'entities': snd_key}]}).sort('score', -1)
                elif lst_qty > 0: 
                        eventX = settings.LAMAEVENT_COLL.find({'date' : event_date, '$or': [{'eventtype':x} for x in evenementen]}).sort('score', -1)
                elif fst_key: 
                        eventX = settings.LAMAEVENT_COLL.find({'date' : event_date, '$or': [{'entities': fst_key}, {'entities': snd_key}]}).sort('score', -1)
                else: 
                        eventX = settings.LAMAEVENT_COLL.find({'date': event_date}).sort([('date', 1), ('score', -1)])

                eventXf = [event for event in eventX if event['cycle'] in periodic_filter]
                if lst_qty > 0:
                        eventXf = [event for event in eventXf if event['eventtype'] in evenementen]
#                               = [event for event in eventXf if event['predicted'] in evenementen]
                eventXf = enrich_events(eventXf) 
                eventObjlist.append(eventXf)

                if eventXf : 
                        foundEventsForDates = True 

        #Combination of this lists helps to find the events of the queried period for calendar.
        allperEventsDictList = [{'dateitem': t[0], 'dateitemstr': t[1], 'eventObj': t[2], 'datetimeitem': t[3]} for t in zip(datelist, dateliststr, eventObjlist, datetimelist)]
        # TODO: Remove empty dates from allperEventDictList
        return allperEventsDictList, foundEventsForDates

class Calendar(View):
        """All the inputs on website are coming here to find results"""

        def get(self, request):
                """
                Calculates the current date and add number of dates which you described with 'timeIntstr' at the beginning. 
                This is working, when you open the main page for the first time.
                """
                #if request.is_mobile:
                #        timeIntstr = timeIntstr_m
                #        time_interval = time_interval_m
                #        template = 'mobile/nextint.mobile.html'
                #else:
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
                periodic_filter = ['periodic','aperiodic']#cycle

                allperEventsDictList, foundEventsForDates = call_dates(now_date, dateLater, periodic_filter) 

                return render(request, template, {
                                'urlprefix': settings.URLPREFIX, #Calls the urlprefix from settings.
                                'allperEventsDictList': allperEventsDictList,
                                'nextDate': nextDate,
                                'nextnextDate': nextnextDate,
                                'prevDate': prevDate,
                                'currDate': currDate,
                                'timeIntstr' : timeIntstr,
                                'foundEventsForDates' : True,
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
#                               event_list = Events.objects(Q(Estimation__gte = start_hour) & Q(Estimation__lte = end_hour)).order_by('Estimation')
                :param fst_key: First Keyterm
                :param snd_key: Second Keyterm
                """

#                if "date_picker" in request.POST:

#                        start_date = request.POST.get('start_date')
#                        end_date = request.POST.get('end_date')
#                        if end_date == '':
#                                end_date = start_date

#                        if request.is_mobile:
 #                               timeIntstr = timeIntstr_m
  #                              time_interval = time_interval_m
   #                             template = 'mobile/datepicker.mobile.html'
    #                    else:
     #                           timeIntstr = timeIntstr_d
      #                          time_interval = time_interval_d
       #                         template = 'desktop/datepicker.html'

        #                startDate = datetime.strptime(start_date, dateformat)
         #               endDate = datetime.strptime(end_date, dateformat)

                        #These are for the navigation links;
          #              nextnext3Date = (endDate + timedelta(days=time_interval)).strftime(dateformat)
           #             prev3Date = (startDate + timedelta(days=-time_interval)).strftime(dateformat)

            #            periodic_filter = ['periodic','aperiodic']
             #           allperEventsDictList = call_dates(startDate, endDate, periodic_filter)

              #          return render(request, template, {
               #                         'urlprefix': settings.URLPREFIX,
                #                        'allperEventsDictList': allperEventsDictList,
                 #                       'start_date': start_date,
                  #                      'end_date': end_date,
                   #                     'nextnext3Date': nextnext3Date,
                    #                    'prev3Date': prev3Date,
                     #   })

                if "ttee" in request.POST:

                        search_hour = request.POST['search_hour']
                        hour_range = request.POST['hour_range']

                        #if request.is_mobile:
                        #        template = 'mobile/ttee.mobile.html'
                        #else:
                        template = 'desktop/ttee.html'

                        if int(search_hour) > int(hour_range): 
                                start_hour = datetime.now() + timedelta(hours=(int(search_hour)-int(hour_range)))
                        else:
                                start_hour = datetime.now() 

                        end_hour = datetime.now() + timedelta(hours=(int(search_hour)+int(hour_range)))#Sometimes a subset of fields on a Document is required, and for efficiency only these should be retrieved from the database. This issue is especially important for MongoDB, as fields may often be extremely large (e.g. a ListField of EmbeddedDocuments, which represent the comments on a blog post. To select only a subset of fields, use only(), specifying the fields you want to retrieve as its arguments. Note that if fields that are not downloaded are accessed, their default value (or None if no default value is provided) will be given:

                        #These are for showing the date interval for the search;
                        startHour = start_hour.strftime("%d %B %Y %H:00")
                        endHour = end_hour.strftime("%d %B %Y %H:00")

                        event_list = settings.LAMAEVENT_COLL.find({'date': {'$gte' : start_hour, '$lte' : end_hour}})
                        event_list = enrich_events([e for e in event_list])
                        return render(request, template, {
                                        'urlprefix': settings.URLPREFIX,
                                        'event_list': event_list,
                                        'startHour': startHour,
                                        'endHour': endHour,
                        })

                elif "event_search" in request.POST:

                        start_date = request.POST.get('start_date') 
                        end_date = request.POST.get('end_date')
                        
                        if end_date == '':
                                end_date = start_date
                        if start_date == '' and end_date != '':
                                start_date = end_date
                        
                        fst_key = request.POST['fst_key']
                        snd_key = request.POST['snd_key']
                        if fst_key == '' and snd_key != '':
                                fst_key = snd_key

                        event_type_dict_nEng = {'Evenement': 'public event', 'Sport': 'sport', 'Sociale actie': 'social action', 'Politiek': 'politics', 'Software': 'software', 'Speciale dag': 'special day', 'Advertentie':'advertisement', 'Uitzending': 'broadcast', 'Anders': 'other'}

                        all_event_types_nDut = ['advertentie', 'politiek', 'evenement', 'sociale_actie', 'software', 'speciale_dag', 'sport', 'uitzending', 'anders']
                        all_event_types_nEng = ['public event', 'politics', 'advertisement', 'social_action', 'software', 'special_day', 'sport', 'broadcast', 'other']

                        checked_event_types = (set(all_event_types_nDut) & set(request.POST.keys()))                        

                        if len(list(checked_event_types)) > 0: 
                                evenementen = [event_type_dict_nEng[request.POST[event_type]] for event_type in checked_event_types]
                        else:
                                evenementen = all_event_types_nEng
                        lst_qty = len(evenementen)

                        if start_date !='':

                                # run the date_picker code to search only for date
                                #if request.is_mobile:
                                #         timeIntstr = timeIntstr_m
                                #         time_interval = time_interval_m
                                #         template = 'mobile/datepicker.mobile.html'
                                #else:
                                timeIntstr = timeIntstr_d
                                time_interval = time_interval_d
                                template = 'desktop/datepicker.html'

                                startDate = datetime.strptime(start_date, dateformat)
                                endDate = datetime.strptime(end_date, dateformat)

                                #These are for the navigation links;
                                nextnext3Date = (endDate + timedelta(days=time_interval)).strftime(dateformat)
                                prev3Date = (startDate + timedelta(days=-time_interval)).strftime(dateformat)

                                periodic_filter = ['periodic','aperiodic']#cycle field
                                
                                allperEventsDictList, foundEventsForDates = call_dates(startDate, endDate, periodic_filter, fst_key, snd_key, evenementen, lst_qty)
                                
                                return render(request, template, {
                                        'urlprefix': settings.URLPREFIX,
                                        'allperEventsDictList': allperEventsDictList,
                                        'start_date': start_date,
                                        'end_date': end_date,
                                        'nextnext3Date': nextnext3Date,
                                        'prev3Date': prev3Date,
                                        'foundEventsForDates' : foundEventsForDates
                                })

                        elif fst_key != '': ##The user didn't selected date, in this case we will run the same code of the zoekwoorden     
                                
                                #if request.is_mobile:
                                #        template = 'mobile/eventSearch.mobile.html'
                                #else:
                                template = 'desktop/eventSearch.html'
                                
                                events_bykey_list = settings.LAMAEVENT_COLL.find({'$or': [{'entities': fst_key}, {'entities': snd_key}]})
                               
                                if lst_qty > 0:
                                        events_bykey_list_types = [event for event in events_bykey_list if event['eventtype'] in evenementen]
                                events_bykey_list_types = enrich_events(events_bykey_list_types)

                                return render(request, template, {
                                        'urlprefix': settings.URLPREFIX,
                                        'events_bykey_list': events_bykey_list_types,
                                        'fst_key': fst_key,
                                        'snd_key': snd_key,
                                        'evenementen' : evenementen
                                })
                         
                                      
                        else:  ##The user didn't select date or enter any keywords##
                                
                                #if request.is_mobile:
                                #        template = 'mobile/non-information.html'
                                #else:
                                template = 'desktop/non-information.html'
                                
                                return render(request, template, {
                                                'urlprefix': settings.URLPREFIX,
                                })

                elif "periodicity_select" in request.POST:

                        periodic_filter = request.POST.getlist('Periodiciteit')

                        #if request.is_mobile:
                        #        timeIntstr = timeIntstr_m
                        #        time_interval = time_interval_m
                        #        template = 'mobile/nextint.mobile.html'
                        #else:
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

                        allperEventsDictList = call_dates(now_date, dateLater, periodic_filter)

                        return render(request, template, {
                                'urlprefix': settings.URLPREFIX, #Calls the urlprefix from settings.
                                'allperEventsDictList': allperEventsDictList,
                                'nextDate': nextDate,
                                'nextnextDate': nextnextDate,
                                'prevDate': prevDate,
                                'currDate': currDate,
                                'timeIntstr' : timeIntstr,
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
                #if request.is_mobile:
                #        timeIntstr = timeIntstr_m
                #        time_interval = time_interval_m
                #        template = 'mobile/intervalseek.mobile.html'
                #else:
                timeIntstr = timeIntstr_d
                time_interval = time_interval_d
                template = 'desktop/intervalseek.html'

                #These are for using the dates which come from links, in call_dates
                currDate2 = datetime.strptime(fst, dateformat)
                dateLater2 = currDate2 + timedelta(days=time_interval)

                #These are for the new navigation links.
                nextnext2Date = (dateLater2 + timedelta(days=time_interval)).strftime(dateformat)
                prev2Date = (currDate2 + timedelta(days=-time_interval)).strftime(dateformat)

                periodic_filter = ['periodic','aperiodic']
                allperEventsDictList, foundEventsForDates = call_dates(currDate2, dateLater2, periodic_filter)                

                return render(request, template, {
                                'urlprefix': settings.URLPREFIX,
                                'allperEventsDictList': allperEventsDictList,
                                'fst': fst,
                                'snd': snd,
                                'nextnext2Date': nextnext2Date,
                                'prev2Date': prev2Date,
                                'foundEventsForDates' : True, 
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
                events_date_list = settings.LAMAEVENT_COLL.find({'date': datetime.strptime(dt, dateformat)})
                events_date_list = enrich_events(events_date_list)

                #Calculates the next and previous days for the navigation links;
                nextDay = (datetime.strptime(dt, dateformat) + timedelta(days=1)).strftime(dateformat)
                prevDay = (datetime.strptime(dt, dateformat) + timedelta(days=-1)).strftime(dateformat)
        
                #if request.is_mobile:
                #        template = 'mobile/events.mobile.html'
                #else:
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

                event = settings.LAMAEVENT_COLL.find({'_id': ObjectId(id)})

                event = enrich_events([e for e in event])[0]

                if event['periodicity']:
                        event['periodicity']['editions'] = list(reversed(event['periodicity']['editions']))

                #if request.is_mobile:
                #        template = 'mobile/eventDetail.mobile.html'
                #else:
                template = 'desktop/eventDetail.html'

                return render(request, template, {
                                'urlprefix': settings.URLPREFIX,
                                'event': event,
                })


class About(View):
        """Redirects links to about pages."""
        def get(self, request, ov):

                #if request.is_mobile:
                #        template = 'mobile/'+ ov +'-lama.mobile.html'
                #else:
                template = 'desktop/'+ ov +'-lama.html'

                return render(request, template, {
                        'urlprefix': settings.URLPREFIX,
                })

class NonInfo(View):
        """Redirects links to non-information page."""
        def get(self, request):

                #if request.is_mobile:
                #        template = 'mobile/'+ ov +'-lama.mobile.html'
                #else:
                template = 'desktop/non-information.html'

                return render(request, template, {
                        'urlprefix': settings.URLPREFIX,
                })

class Error404(View):
        """This view shows 404 page."""
        def get(self, request):

                #if request.is_mobile:
                #        template = 'mobile/'+ ov +'-lama.mobile.html'
                #else:
                template = 'desktop/404.html'

                return render(request, template, {
                        'urlprefix': settings.URLPREFIX,
                })

class Error500(View):
        """This view shows 500 page."""
        def get(self, request):

                #if request.is_mobile:
                #        template = 'mobile/'+ ov +'-lama.mobile.html'
                #else:
                template = 'desktop/500.html'

                return render(request, template, {
                        'urlprefix': settings.URLPREFIX,
                })


def custom_handler_404(request):
    return render(request, 'desktop/404.html')

def custom_handler_500(request):
    return render(request, 'desktop/500.html')


# line 116 
#                        eventX = Events.objects(Q(date=i) & (Q(entities__iexact=fst_key) | Q(entities__iexact=snd_key))).order_by('-score')
#################################################################################################################################################################################
# line 118 
#                        eventX = Events.objects(date=i).order_by('-score')
#################################################################################################################################################################################
# line 296
#                        event_list = Events.objects(Q(date__gte = start_hour) & Q(date__lte = end_hour)).order_by('date')
######################################################################################################################################################################
# line 354 
                                #events_bykey_list = Events.objects(Q(Estimation__gte = datetime.now()) & (Q(keylist__iexact=fst_key) | Q(keylist__iexact=snd_key))).order_by('Estimation')
                                #events_bykey_list = Events.objects((Q(keylist__iexact=fst_key) | Q(keylist__iexact=snd_key)))
                                
#                                events_bykey_list = Events.objects((Q(entities__iexact=fst_key) | Q(entities__iexact=snd_key)))
#################################################################################################################################################################################
# line 475
#                events_date_list = Events.objects(date=datetime.strptime(dt, dateformat)).order_by('-score')
#########################################################################################################################################################################
# line 506
#                event = Events.objects.get(pk=id)
########################################################################################################################################################################
# Unique list
# Python program to check if two 
# to get unique values from list
# using traversal 

# function to get unique values
#def unique(list2):

	# intilize a null list
#	unique_list = []
	
	# traverse for all elements
#	for x in list2:
		# check if exists in unique_list or not
#		if x not in unique_list:
#			unique_list.append(x)
	# print list
#	for x in unique_list:
#		print x,
	


# driver code
#list1 = [10, 20, 10, 30, 40, 40]
#print("the unique values from 1st list is")
#unique(list1)


#list2 =[1, 2, 1, 1, 3, 4, 3, 3, 5, 4, 40, 6, 3, 6]
#print("\nthe unique values from 2nd list is")
#unique(list2)
##########################################################################################################################################################################

