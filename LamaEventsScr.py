"""
!!!WARNING!!!: This docstrings are basically useless, If you want to change them on documentation, change the LamaeventsScr.rst file manually!

The Program flow is as follows:
  1- Connect to MongoDB (MangoLab)
  2- Retrieve tweets from twiqs.nl every hour.
  3- Call the event detection.
  4- Clear the former results from the database.
  5- Run the time-to-event estimation module.
  6- Write the new results to database, after each time-to-event estimation. 


Trouble Shooting:
 - The url for twiqs.nl may change from time to time.
 - Twiqs.nl may not provide tweets in time. Therefore this particular hour will not be taken into account.

"""

import configparser

import requests
import random

import time
from datetime import date, datetime, timedelta

import pymongo

import DEvents.event_pairs as event_pairs


#Get all the private configurations;
config = configparser.ConfigParser()
config.read('/home/ebasar/oauth.ini')

#MongoLab OAuth;
client_host = config.get('LE_script_db', 'client_host')
client_port = int(config.get('LE_script_db', 'client_port'))
db_name = config.get('LE_script_db', 'db_name')
user_name = config.get('LE_script_db', 'user_name')
passwd = config.get('LE_script_db', 'passwd')

#Twiqs OAuth;
user_name2 = config.get('LE_script_twiqs', 'user_name')
passwd2 = config.get('LE_script_twiqs', 'passwd')


#!IDEA! = Add try-except block for the connection part;
#MongoLab Connection;
connection = pymongo.MongoClient(client_host, client_port)
ledb = connection[db_name] #Database
ledb.authenticate(user_name, passwd)
lecl = ledb.lecl #Collection
print("Connected to DB")


ep = event_pairs.Event_pairs("all","coco_out/","tmp/")
print("Event Detection Initialised")


#Get the cookie for twiqs.nl;
s = requests.Session()
r = s.post("http://145.100.57.182/cgi-bin/twitter", data={"NAME":user_name2, "PASSWD":passwd2})


#!IDEA! = Argparser can be used to get system parameters;
#Twiqs.nl parameters;
payload = {'SEARCH': 'echtalles', 'DATE': 'yyyymmddhh-yyyymmddhh', 'DOWNLOAD':True, 'SHOWTWEETS':True}
#DATE = <start,end> --> start and end should point to the same hour in order to get tweets about an hour


def RequestTweets():
	"""
	Fetches the tweets from twiqs.nl
	Warning = The url may need to be updated from time to time!
	"""
	output1st = requests.get("http://145.100.57.182/cgi-bin/twitter", params=payload, cookies=s.cookies)
	return output1st


#If True, don't contain details of tweets except ids and users. Also don't contain the keyterms of events after keeping them in keylist.
DeleteTweetDetails = True

#If True, delete the former events from mongo db.
DeleteFormerEvents = True

while True:
	time.sleep(120) #Check every two minutes if you are in the next hour.

	#Time Calculations;
	nowDate = datetime.now()
	nowDate_earlier = nowDate - timedelta(hours=1) #Get the previous hour. Because you can get tweets for the last hour from twiqs.nl.
	tweethour = nowDate_earlier.strftime("%H:00 %d-%m-%Y") #Just for showing off the hour which tweets requested.
	nes = nowDate_earlier.strftime("%Y%m%d%H") #'yyyymmddhh' twiqs.nl format.
	pDate = nes+'-'+nes #Twiqs.nl needs this format. Start and end time should be the same to retrieve tweets for one hour.
	currTime = nowDate.strftime("%H:%M") #Just for showing off the minutes while waiting for the next hour.

	#Check if we are still in the same hour:
	if payload['DATE'] == pDate: #Continue waiting if you are in the same hour. Otherwise process the next hour.
		print(currTime)
		continue
	else:
		payload['DATE'] = pDate #It will remain the same until next hour.
		print("Tweet hour : " + tweethour)

		#Request to Twiqs;
		output = RequestTweets()
		print("Request Completed")

		#Check the cookie;
		withoutcookie = '#user_id\t#tweet_id\t#DATE='+pDate+'\t#SEARCHTOKEN=echtalles\n'
		if output.text[:70] == withoutcookie: #if the cookie doesn't have access right to download the tweets, it will skip this hour.
			print("Cookie is wrong. I'll skip tweets at " + tweethour + "You have to check your cookie configuration!")
			#!IDEA! = If the cookie is wrong, write the code(call the relevant method) for getting a new one here.
			continue
		else:
			print("Cookie is Fine.")

		#Check the result of request;
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

		#Event Detection; (refer to Florian Kunneman for any issue)
		EventDic = ep.detect_events(output.text[:-1]) # [:-1] = ignoring the last '\n' at the bottom of the file.
		print("Event Detection Completed")

		if DeleteFormerEvents:
			lecl.remove({ }) #Delete the old events from database
			print("Former events are deleted from the database")

		for k,v in EventDic.items(): #For every detected event

			#TimeToEventEstimation Calculations;
			createDate = datetime.now() #TTE Estimation will be added to the current time
			randomTTE = random.uniform(0.0, 193.0) #random number for estimation (for now)
			hh, premm = divmod(randomTTE, 1)
			mm = (60*premm)*0.1
			v['Estimation'] = createDate + timedelta(hours=int(hh), minutes=int(mm))

			#Convert date formats to datetime format;
			#To avoid this error : "bson.errors.InvalidDocument: Cannot encode object: datetime.date(2015, 6, 3)"
			v['date'] = datetime.combine(v['date'], datetime.min.time())

			#Writing keyterms in a list without keyterm scores; (In django using this list is more efficient)
			v['keylist'] = []
			for m in v['keyterms']:
				mt = m[0].title() #capitalization
				v['keylist'].append(mt)

			if DeleteTweetDetails:
				del v['keyterms']
				for i in v['tweets']:
					del i['date'], i['date references'], i['text'], i['entities']
			else:
				#If you don't delete details; convert date formats to datetime format;
				for i in v['tweets']:
					i['date'] = datetime.combine(i['date'], datetime.min.time())

			#Write to database event by event;
			lecl.insert(v) 
		print("Written to Database")

		continue


