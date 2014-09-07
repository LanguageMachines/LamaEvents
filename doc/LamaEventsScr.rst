Lama Events Python Script
====================

Here the whole code explained line by line.

:The Program flow is as follows:
  1. Connect to MongoDB (MangoLab)
  2. Retrieve tweets from twiqs.nl every hour.
  3. Call the event detection.
  4. Clear the former results from the database.
  5. Run the time-to-event estimation module.
  6. Write the new results to database, after each time-to-event estimation. 


:Trouble Shooting:
 - The URL for twiqs.nl may change from time to time.
 - Twiqs.nl may not provide tweets in time. Therefore this particular hour will not be taken into account.

You can reach this script from `GitHub <https://github.com/ErkanBasar/LamaEvents/blob/master/LamaEvents.py/>`_

Beginning
-----------------------


.. rubric:: Imports;

Here we are using these::

	import configparser
	import requests
	import random
	import time
	from datetime import date, datetime, timedelta
	import pymongo

The following code imports a script developed by Florian Kunneman::

	import DEvents.event_pairs as event_pairs

.. warning:: To use Event Detection code, you have to clone `DEvents <https://github.com/fkunneman/DEvents/>`_ and the requirements of that. Refer to Florian Kunneman for any issue about DEvents.


.. rubric:: Private things;

All the private configurations is in another file. You have to read it first with ConfigParser()::

	config = configparser.ConfigParser()
	config.read('/home/ebasar/oauth.ini')

And then you can reach the configurations with following codes::

	#MongoLab connection authentications;
	client_host = config.get('LE_script_db', 'client_host')
	client_port = int(config.get('LE_script_db', 'client_port'))
	db_name = config.get('LE_script_db', 'db_name')
	user_name = config.get('LE_script_db', 'user_name')
	passwd = config.get('LE_script_db', 'passwd')

	#Twiqs.nl authentications;
	user_name2 = config.get('LE_script_twiqs', 'user_name')
	passwd2 = config.get('LE_script_twiqs', 'passwd')



.. rubric:: Connect to Database;
::

	connection = pymongo.MongoClient(client_host, client_port)
	ledb = connection[db_name] #Database
	ledb.authenticate(user_name, passwd)
	lecl = ledb.lecl #lecl: Collection
	print("Connected to DB")
	#!IDEA! = Add try-except block for the connection part




.. rubric:: Initialize the Event Detection code;
::

	ep = event_pairs.Event_pairs("all","coco_out/","tmp/")
	print("Event Detection Initialized")



.. rubric:: Get the cookie for twiqs.nl;

Here the cookie is generated automatically. After that we can find cookies with saying 's.cookies'::

	s = requests.Session()
	r = s.post("http://145.100.57.182/cgi-bin/twitter", data={"NAME":user_name2, "PASSWD":passwd2})




.. rubric:: Requesting the tweets;

This dictionary defines the search on twiqs.nl. It points all the tweets for one hour::

	payload = {'SEARCH': 'echtalles', 'DATE': 'start-end', 'DOWNLOAD':True, 'SHOWTWEETS':True}
	#!IDEA! = Argparser can be used to get system parameters in payload.

.. note:: DATE = <start,end> --> start and end should point to the same hour in order to get tweets about an hour and it should be formed like 'yyyymmddhh'.


When the following method called for the first time, it starts a search at the twiqs.nl according to parameters you give to the link with 'payload'. When the search is done you can call it again and fetch the tweets as result::

	def RequestTweets():
		output1st = requests.get("http://145.100.57.182/cgi-bin/twitter", params=payload, cookies=s.cookies)
		return output1st

.. warning:: The url may need to be updated from time to time!




.. rubric:: Extras;

If True, don't contain details of tweets except ids and users. Also don't contain the keyterms of events after keeping them in keylist::

	DeleteTweetDetails = True

If True, delete the former events from mongo db::

	DeleteFormerEvents = True




Inside the Forever Loop
-------------------------

After all configurations set up and all method defined, program goes into a forever loop where it will check the time every 2 minutes and do the all important thing every hour.::

	while True:
		time.sleep(120) #Check every two minutes if you are in the next hour.




.. rubric:: Time Calculations

Here the big deal is calculation of pDate. Because pDate will help to check the hour::

		nowDate = datetime.now()
		#Get the previous hour. Because you can get tweets for the last hour from twiqs.nl.
		nowDate_earlier = nowDate - timedelta(hours=1) 
		#'yyyymmddhh' twiqs.nl format.
		nes = nowDate_earlier.strftime("%Y%m%d%H") 
		#Twiqs.nl needs this format. Start and end time should be the same to retrieve tweets for one hour.
		pDate = nes+'-'+nes 
		#Just for showing off the hour which tweets requested;
		tweethour = nowDate_earlier.strftime("%H:00 %d-%m-%Y") 
	 	#Just for showing off the minutes while waiting for the next hour;
		currTime = nowDate.strftime("%H:%M")



	
.. rubric:: Check the Hour

If the pDate value is equal to payload['DATE'], it means we are still in the same hour.
Here the payload['DATE'] contains the date which we use it for requesting the last tweets in twiqs.nl::

		if payload['DATE'] == pDate: 
			print(currTime)
			continue

If the pDate is not equal the hour of the last tweet request, it means we are in the new hour and there must be new tweets in twiqs.nl.
It'll assign the pDate to payload['DATE'], so the new request will be done with the new date value::

		else:
			payload['DATE'] = pDate #It will remain the same until next hour.
			print("Tweet hour : " + tweethour)




.. rubric:: Request to Twiqs.nl

Since we are in the new hour, time to request for the new tweets. This is first request and starts the search for the new tweets in twiqs.nl::

			output = RequestTweets()
			print("Request Completed")


We have to check the cookie first. if the cookie does not have access right to download the tweets, it will skip this hour and start to wait for the next hour::

			withoutcookie = '#user_id\t#tweet_id\t#DATE='+pDate+'\t#SEARCHTOKEN=echtalles\n'
			if output.text[:70] == withoutcookie: 
				print("Cookie is wrong. I'll skip tweets at " + tweethour + "You have to check your cookie configuration!")
				continue
			else:
				print("Cookie is Fine.")

			#!IDEA! = If the cookie is wrong, write the code(call the relevant method) for getting a new one here.

.. note:: 'withoutcookie' contains the first 70 characters of the string which we will have without the right cookie.

Mostly the search at the twiqs.nl doesn't complete immediatelly after the  first request, therefore there will not be any tweet as result. Here we check the result of the first request and if it is empty, we call a second request for the same subject after waiting 300 second (5 minutes). Then we check the results again, still if there isn't any tweet we skip this hour to protect the previous data in the database::

			dumpoutput = '#user_id\t#tweet_id\t#date\t#time\t#reply_to_tweet_id\t#retweet_to_tweet_id\t#user_name\t#tweet\t#DATE='+pDate+'\t#SEARCHTOKEN=echtalles\n'
			if output.text[:1000] == dumpoutput: #If there isn't any tweet try the request again.
				print("No tweet found at the first time! I'll try again")
				time.sleep(300) #Wait for the search done at twiqs.nl before the next request
				output = RequestTweets()
				if output.text[:1000] == dumpoutput: #If there isn't any tweet again, it will skip this hour.
					print("Still there is not any tweet! I'll skip tweets at " + tweethour)
					continue
				else:
					print("Tweets came at the second time")
			else:
				print("Tweets are O.K.")

.. note:: 'dumpoutput' contains the first line of the tweet file from twiqs.nl. If the first 1000 charachters of output is equal to dumpoutput, it means output is empty and there isn't any tweet.




.. rubric:: Event Detection

Here we call the event detection method from DEvents script to find the new event from the new tweets::

			EventDic = ep.detect_events(output.text[:-1]) # [:-1] = ignoring the last '\n' at the bottom of the file.
			print("Event Detection Completed")




.. rubric:: Deletion for Replacement

With the following code, we delete the old event datas from database to refresh with the new ones::

			if DeleteFormerEvents:
				lecl.remove({ }) #Delete the old events from database
				print("Former events are deleted from the database")

.. note:: remove() is a pymongo method and 'lecl' is the collection name.




.. rubric:: Database Modification

With  the help of this for loop, we are reading the events, make the following modifications and write them to database one by one. 
Everything after that is working in this for loop:: 
	
			for k,v in EventDic.items():

.. note:: v is pointing events.



.. rubric:: Time-To-Event Estimation

The following codes make a random prediction for the events for now. And writes to database on an attribute named 'Estimation'::

				#TimeToEventEstimation Calculations;
				createDate = datetime.now() #TTE Estimation will be added to the current time
				randomTTE = random.uniform(0.0, 193.0) #random number for estimation (for now)
				hh, premm = divmod(randomTTE, 1)
				mm = (60*premm)*0.1
				v['Estimation'] = createDate + timedelta(hours=int(hh), minutes=int(mm))





.. rubric:: Date to Datetime

As a result of event detection, there is an event date data formatted with 'date'. 
But we can't write this data to database like that because of an error. Therefore we convert the date format to datetime format::

				v['date'] = datetime.combine(v['date'], datetime.min.time())
	
.. note:: The error : "bson.errors.InvalidDocument: Cannot encode object: datetime.date(2015, 6, 3)"





.. rubric:: Making a Keylist

Normally as a result of event detection there is a keyterms list with scores in it. 
Since we are not using the scores we are creating a new keyterms list with only keyterms. And this new list makes querying easier and better in Django::

				v['keylist'] = []
				for m in v['keyterms']:
					mt = m[0].title() #capitalization
					v['keylist'].append(mt)
	

.. rubric:: Delete Some Data

Here we delete the old keyterms list of events and some attributes of tweets of events we don't need. 
If the DeleteTweetDetails value is not True, it only makes the same convertion for date value of tweets we did for the events before:: 

				if DeleteTweetDetails:
					del v['keyterms']
					for i in v['tweets']:
						del i['date'], i['date references'], i['text'], i['entities']
				else:
					for i in v['tweets']:
						i['date'] = datetime.combine(i['date'], datetime.min.time())

.. rubric:: Write to Database
::

				lecl.insert(v) 
			print("Written to Database")
	
.. note:: insert() is a pymongo method and 'lecl' is the collection name.




.. automodule:: LamaEventsScr
    :members:
    :undoc-members:
    :show-inheritance:
