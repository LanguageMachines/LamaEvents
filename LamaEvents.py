import requests
import random

import time
import datetime as datetime

import pymongo
from pymongo import MongoClient

import DEvents.event_pairs as event_pairs

#MongoLab Connection;
connection = MongoClient("XXX", XXX)
ledb = connection["XXX"]
ledb.authenticate("XXX", "XXX")
lecl = ledb.lecl
print("Connected to DB")

ep = event_pairs.Event_pairs()
print("Event Detection Initialised")

payload = {'SEARCH': 'echtalles', 'DATE': 'yymmddhh-yymmddhh', 'DOWNLOAD':True, 'SHOWTWEETS':True}

def RequestTweets():
	output1st = requests.get("http://145.100.57.182/cgi-bin/twitter", params=payload, cookies={'cookie':'XXX'})
	return output1st

#To run this, make sure you wrote 'True';
DeleteTweetDetails = 'True'

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
				print("Still there is not any tweet! I'll skip tweets at " + tweethour)
				continue
			else:
				print("Tweets came at the second time")
		else:
			print("Tweets are O.K.")
		#Event Detection;
		EventDic = ep.detect_events(output.text[:-1]) # [:-1] = ignoring the last '\n' at the bottom of the file.
		print("Event Detection Completed")
		for k,v in EventDic.items():
			#TimeToEventEstimation Calculations;
			createDate = datetime.datetime.now()
			randomTTE = random.uniform(0.0, 193.0) #random number for estimation (for now)
			hh, premm = divmod(randomTTE, 1)
			mm = (60*premm)*0.1
			v['getRandomTTE'] = randomTTE
			v['createDate'] = createDate
			v['Estimation'] = createDate + datetime.timedelta(hours=int(hh), minutes=int(mm))
			#Dates to Datetime;
			v['date'] = datetime.datetime.combine(v['date'], datetime.datetime.min.time())
			if DeleteTweetDetails == 'True':
				#Deleting the tweet details;
				for i in v['tweets']:
					del i['date'], i['date references'], i['text'], i['entities']
			else:
				#Tweet dates to datetime;
				for i in v['tweets']:
					i['date'] = datetime.datetime.combine(i['date'], datetime.datetime.min.time())
			#Write to Database;
			lecl.insert(v) 
		print("Written to Database")
		continue


