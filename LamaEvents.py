import configparser

import requests
import random

import time
from datetime import date, datetime, timedelta

import pymongo

import DEvents.event_pairs as event_pairs

#Get all the private configurations;
config = configparser.ConfigParser()
config.read('/media/Data/oauth.ini')

client_host = config.get('LE_script_db', 'client_host')
client_port = int(config.get('LE_script_db', 'client_port'))
db_name = config.get('LE_script_db', 'db_name')
user_name = config.get('LE_script_db', 'user_name')
passwd = config.get('LE_script_db', 'passwd')

user_name2 = config.get('LE_script_twiqs', 'user_name')
passwd2 = config.get('LE_script_twiqs', 'passwd')

#MongoLab Connection;
connection = pymongo.MongoClient(client_host, client_port)
ledb = connection[db_name]
ledb.authenticate(user_name, passwd)
lecl = ledb.lecl
print("Connected to DB")

ep = event_pairs.Event_pairs("all","coco_out/","tmp/")
print("Event Detection Initialised")

#Get the cookie;
s = requests.Session()
r = s.post("http://145.100.57.182/cgi-bin/twitter", data={"NAME":user_name2, "PASSWD":passwd2})

payload = {'SEARCH': 'echtalles', 'DATE': 'yymmddhh-yymmddhh', 'DOWNLOAD':True, 'SHOWTWEETS':True}

def RequestTweets():
	output1st = requests.get("http://145.100.57.182/cgi-bin/twitter", params=payload, cookies=s.cookies)
	return output1st

#To run this, make sure you wrote 'True';
DeleteTweetDetails = 'True'

while True:
	time.sleep(60)
	#Time Calculations;
	nowDate = datetime.now()
	nowDate_earlier = nowDate - timedelta(hours=1)
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
			createDate = datetime.now()
			randomTTE = random.uniform(0.0, 193.0) #random number for estimation (for now)
			hh, premm = divmod(randomTTE, 1)
			mm = (60*premm)*0.1
			#v['getRandomTTE'] = randomTTE
			#v['createDate'] = createDate
			v['Estimation'] = createDate + timedelta(hours=int(hh), minutes=int(mm))
			#Dates to Datetime;
			v['date'] = datetime.combine(v['date'], datetime.min.time())
			#Writing keyterms in a list without scores;
			v['keylist'] = []
			for m in v['keyterms']:
				mt = m[0].title() #capitalization
				v['keylist'].append(mt)
			if DeleteTweetDetails == 'True':
				#Deleting the tweet details;
				del v['keyterms']
				for i in v['tweets']:
					del i['date'], i['date references'], i['text'], i['entities']
			else:
				#Tweet dates to datetime;
				for i in v['tweets']:
					i['date'] = datetime.combine(i['date'], datetime.min.time())
			#Write to Database;
			lecl.insert(v) 
		print("Written to Database")
		continue


