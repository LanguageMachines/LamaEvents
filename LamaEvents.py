import requests

import pymongo
from pymongo import MongoClient

import time
import datetime as datetime

import DEvents.event_pairs as event_pairs

#MongoLab Connection;
connection = MongoClient("XXX", XXX)
ledb = connection["XXX"]
ledb.authenticate("XXX", "XXX")
lecl = ledb.lecl
print("Connected to DB")

ep = event_pairs.Event_pairs()
print("Event Detection Initialised")

payload = {'SEARCH': 'echtalles', 'DATE': '2014081214-2014081214', 'DOWNLOAD':True, 'SHOWTWEETS':True}

def RequestTweets():
#Add an automatic cookie finder here (requests.Session())
	output1st = requests.get("http://145.100.57.182/cgi-bin/twitter", params=payload, cookies={'cookie':'XXX'})
	return output1st


while True:
	time.sleep(600)
	#Time Calculations;
	nowDate = datetime.datetime.now()
	nowDate_earlier = nowDate - datetime.timedelta(hours=1)
	tweethour = nowDate_earlier.strftime("%H:00 %d-%m-20%y")
	nes = nowDate_earlier.strftime("20%y%m%d%H")
	pDate = nes+'-'+nes
	b = nowDate.strftime("%H:%M")
	#Check if we are still in the same hour:
	if payload['DATE'] == pDate:
		print(b)
		continue
	else:
		payload['DATE'] = pDate
		print("Tweet hour : " + tweethour)
		#Request to Twiqs;
		output = RequestTweets()
		print("Request Completed")
		#Check the cookie;
		withoutcookie = '#user_id\t#tweet_id\t#DATE='+pDate+'\t#SEARCHTOKEN=echtalles\n'
		if output.text[:70] == withoutcookie:
			print("Cookie is wrong. I'll skip tweets at " + tweethour + "But you have to change your cookie!")
			continue
		else:
			print("Cookie is Fine.")
		#Check the result of request;
		dumpoutput = '#user_id\t#tweet_id\t#date\t#time\t#reply_to_tweet_id\t#retweet_to_tweet_id\t#user_name\t#tweet\t#DATE='+pDate+'\t#SEARCHTOKEN=echtalles\n'
		if output.text[:1000] == dumpoutput:
			print("No tweet found at the first time! I'll try again")
			time.sleep(300)
			output = RequestTweets()
			if output.text[:1000] == dumpoutput:
				print("Still there is no tweet! I'll skip tweets at " + tweethour)
				continue
			else:
				print("Tweets came at the second time")
		else:
			print("Tweets are O.K.")
		#Event Detection;
		EventDic = ep.detect_events(output.text[:-1]) # [:-1] = ignoring the last '\n' at the bottom of the file.
		print("Event Detection Completed")
		#Date to Datetime;
		for k,v in EventDic.items():
			v['date'] = datetime.datetime.combine(v['date'], datetime.datetime.min.time())
			for i in v['tweets']:
				i['date'] = datetime.datetime.combine(i['date'], datetime.datetime.min.time())
			lecl.insert(v) #Writing to Database
		print("Written to Database")
	#Add here some break for  too long processes
		continue



