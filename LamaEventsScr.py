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


Usage;

You van define this variables as minutes;
 -'looptime' is waiting time for every loop
 -'requestwait' is waiting time for the next request

All loggings are written to 'LamaEvents.log'
You can see the last loggings with this command line code::

	>> tail -F Lamaevents.log 

"""

import sys
import time
import random
import smtplib 
import pymongo
import logging
import requests
import configparser
from datetime import date, datetime, timedelta

import DEvents.event_pairs as event_pairs


#!HINT! : Change this variables to decide to waiting times (use minutes)
looptime = 2
requestwait = 2


#Logging Configurations;
logging.basicConfig(
		format='%(asctime)s, %(levelname)s: %(message)s',
		filename='LamaEvents.log',
		datefmt='%d-%m-%Y, %H:%M',
		level=logging.INFO)

logging.info('Lama Events Script Started')


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


#Sends mail to 'toaddrs' about warnings and errors.
def send_mail(msg):
	toaddrs  = 'mustafaerkanbasar@gmail.com' 
	#Mail OAuth;
	fromaddr = config.get('LE_script_mail', 'fromaddr')   
	username = config.get('LE_script_mail', 'user_name') 
	password = config.get('LE_script_mail', 'password')
	subject = "Lama Events"
	message = 'Subject: %s\n\n%s' % (subject, msg)
	server = smtplib.SMTP('smtp.gmail.com:587')  
	server.starttls()  
	server.login(username,password)  
	server.sendmail(fromaddr, toaddrs, message)  
	server.quit()  



#!IDEA! = Add try-except block for the connection part;
#MongoLab Connection;
try:
	connection = pymongo.MongoClient(client_host, client_port)
	ledb = connection[db_name] #Database
	ledb.authenticate(user_name, passwd)
	lecl = ledb.lecl #Collection
	logging.info('Connected to DB')
except Exception:
	logging.error("Database Connection Failed. Script Stopped.")
	send_mail("Lama Events Error : Database Connection Failed. Script Stopped.")
	sys.exit("Error : Database Connection Failed!")
	pass


ep = event_pairs.Event_pairs("all","coco_out/","tmp/")
logging.info('Event Detection Initialised')


#Get the cookie for twiqs.nl;
s = requests.Session()
r = s.post("http://145.100.57.182/cgi-bin/twitter", data={"NAME":user_name2, "PASSWD":passwd2})
logging.info('Cookie Created')


#Twiqs.nl parameters;
payload = {'SEARCH': 'echtalles', 'DATE': 'yyyymmddhh-yyyymmddhh', 'DOWNLOAD':True, 'SHOWTWEETS':True}
#DATE = <start,end> --> start and end should point to the same hour in order to get tweets about an hour
#!IDEA! = Argparser can be used to get system parameters


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

timereminder = 0

while True:
	time.sleep(60*looptime) #Check every <looptime> minutes if you are in the next hour.

	#Time Calculations;
	nowDate = datetime.now()
	nowDate_earlier = nowDate - timedelta(hours=1) #Get the previous hour. Because you can get tweets for the last hour from twiqs.nl.
	tweethour = nowDate_earlier.strftime("%H:00") #Just for showing off the hour which tweets requested.
	nes = nowDate_earlier.strftime("%Y%m%d%H") #'yyyymmddhh' twiqs.nl format.
	pDate = nes+'-'+nes #Twiqs.nl needs this format. Start and end time should be the same to retrieve tweets for one hour.

	#Every 5th time remind the current situation;
	timereminder += 1
	if timereminder == 5:
		logging.info('Waiting for the next hour')

	#Continue waiting if you are in the same hour. Otherwise process the next hour:
	if payload['DATE'] == pDate: 
		continue
	else:
		payload['DATE'] = pDate #It will remain same until next hour.
		logging.info('Tweet hour : '+ tweethour)

		#Reset the time reminder;
		timereminder = 0

		#Request to Twiqs;
		output = RequestTweets()
		logging.info('First Request Completed')


		#Check the cookie;
		withoutcookie = '#user_id\t#tweet_id\t#DATE='+pDate+'\t#SEARCHTOKEN=echtalles\n'
		if output.text[:70] == withoutcookie: #if the cookie doesn't have access right to download the tweets, it will skip this hour.
			logging.warning("Cookie doesn't have access right to download. It skipped the tweets at " + tweethour + '. You have to check your cookie configuration!')
			send_mail("Lama Events Warning : Cookie doesn't have access right to download. It skipped the tweets at " + tweethour)
			#!IDEA! = If the cookie is wrong, write the code(call the relevant method) for getting a new one here.
			continue
		else:
			logging.info('Cookie is Fine')


		#Check the result of request;
		dumpoutput = '#user_id\t#tweet_id\t#date\t#time\t#reply_to_tweet_id\t#retweet_to_tweet_id\t#user_name\t#tweet\t#DATE='+pDate+'\t#SEARCHTOKEN=echtalles\n'
		if output.text[:1000] == dumpoutput: #If there isn't any tweet try the request again for 10 times.
			logging.info("There isn't any tweet yet. Starting to request tweets every "+ str(requestwait) +" minutes, maximum 15 times")
			for i in range(0,15):
				time.sleep(60*requestwait) #Wait for the search done at twiqs.nl before the next request
				output = RequestTweets()
				if output.text[:1000] == dumpoutput: #If there isn't any tweet again, it will skip this hour.
					logging.info('No tweet at ' + str(i))
					continue
				else:
					logging.info('Tweets came on '+ str(i))
					break
		else:
			logging.info('Tweets are O.K.')


		#Check the results one last time if there isn't any tweet send an e-mail;
		if output.text[:1000] == dumpoutput: #If there isn't any tweet again, it will skip this hour.
			logging.warning('Still there is not any tweet! It skipped the tweets at '+ tweethour)
			send_mail("Lama Events Warning : There isn't any tweet for this hour from twiqs.nl :" + tweethour)
			continue


		#Event Detection; (refer to Florian Kunneman for any issue)
		EventDic = ep.detect_events(output.text[:-1]) # [:-1] = ignoring the last '\n' at the bottom of the file.
		logging.info('Event Detection Completed')

		if DeleteFormerEvents:
			lecl.remove({ }) #Delete the old events from database
			logging.info('Former events are deleted from the database')

		for k,v in EventDic.items(): #For every detected event

			#TimeToEventEstimation Calculations;
			createDate = datetime.now() #TTE Estimation will be added to the current time
			randomTTE = random.uniform(0.0, 193.0) #random number for estimation (for now)
			hh, premm = divmod(randomTTE, 1)
			mm = (60*premm)*0.1
			v['Estimation'] = createDate + timedelta(hours=int(hh), minutes=int(mm))

			#Convert date formats to datetime format;
			#to avoid this error : "bson.errors.InvalidDocument: Cannot encode object: datetime.date(2015, 6, 3)"
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
				logging.info("Tweet Details Deleted")
			else:
				#If you don't delete details; convert date formats to datetime format;
				for i in v['tweets']:
					i['date'] = datetime.combine(i['date'], datetime.min.time())

			#Write to database event by event;
			lecl.insert(v) 
		logging.info('Written to Database')



