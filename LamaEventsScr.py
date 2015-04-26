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

You can define this variables as minutes;
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
import event_pairs
import calculations

#!HINT! : Change this variables to decide to waiting times (use minutes)
looptime = 1
requestwait = 2
requestloop = int(30/requestwait)


#Logging Configurations;
logging.basicConfig(
		format='%(asctime)s, %(levelname)s: %(message)s',
		filename='LamaEvents.log',
		datefmt='%d-%m-%Y, %H:%M',
		level=logging.INFO)

logging.info('Lama Events Script Started')


#Get all the private configurations;
config = configparser.ConfigParser()
config.read('/scratch/fkunneman/lamaevents/oauth.ini')

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
	#Mail OAuth;
	fromaddr = config.get('LE_script_mail', 'fromaddr')   
	toaddrs  = config.get('LE_script_mail', 'florian') #to address options = hurrial, florrian, antalb, ebasar
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
	#ledb.authenticate(user_name, passwd)
	lecl = ledb.lecl #Collection
	logging.info('Connected to DB')
except Exception:
	logging.error("Database Connection Failed. Script Stopped.")
	send_mail("Lama Events Error : Database Connection Failed. Script Stopped.")
	sys.exit("Error : Database Connection Failed!")
	pass

ep = event_pairs.Event_pairs("coco_out/","tmp/",f = True,cities = "citylist_all-nl.txt")
logging.info('Event Detection Initialised')

#Get the cookie for twiqs.nl;
s = requests.Session()
r = s.post("http://145.100.58.245/cgi-bin/twitter", data={"NAME":user_name2, "PASSWD":passwd2})
logging.info('Cookie Created')


#Twiqs.nl parameters;
payload = {'SEARCH': 'echtalles', 'DATE': 'yyyymmddhh-yyyymmddhh', 'DOWNLOAD':True, 'SHOWTWEETS':True}
payload_lost = {'SEARCH': 'echtalles', 'DATE': 'yyyymmddhh-yyyymmddhh', 'DOWNLOAD':True, 'SHOWTWEETS':True}
#DATE = <start,end> --> start and end should point to the same hour in order to get tweets about an hour
#!IDEA! = Argparser can be used to get system parameters

#load info on missed files
lost_tweets = []
with open("tmp/lostevents.txt") as f: 
	lost_tweets = [x.strip() for x in f.readlines()]
	f.close()

def RequestTweets(t):
	"""
	Fetches the tweets from twiqs.nl
	Warning = The url may need to be updated from time to time!
	"""
	try:
		output1st = requests.get("http://145.100.58.245/cgi-bin/twitter", params=t, cookies=s.cookies)
#		print("output1st",output1st)
	except:
		print("output1st = false")
		output1st = False
	return output1st


def event_procedure(d,e=True):
	print(d)
	print("fetching",d['DATE'],"from twiqs")
	#payload['DATE'] = pDate #It will remain same until next hour.
	logging.info('Tweet hour : '+ d['DATE'])

	#Reset the time reminder;
	timereminder = 0

	success = True
	#Request to Twiqs;
	output = False
	while not output:
		output = RequestTweets(d)
	logging.info('First Request Completed')


	#Check the cookie;
	#withoutcookie = '#user_id\t#tweet_id\t#DATE='+pDate+'\t#SEARCHTOKEN=echtalles\n'
	#if output.text[:70] == withoutcookie: #if the cookie doesn't have access right to download the tweets, it will skip this hour.
#		logging.warning("Cookie doesn't have access right to download. It skipped the tweets at " + tweethour + '. You have to check your cookie configuration!')
#		send_mail("Lama Events Warning : Cookie doesn't have access right to download. It skipped the tweets at " + tweethour)
#		continue
		#!IDEA! = If the cookie is wrong, write the code(call the relevant method) for getting a new one here.
#	else:
#		logging.info('Cookie is Fine')


	#Check the result of request;
	dumpoutput = '#user_id\t#tweet_id\t#date\t#time\t#reply_to_tweet_id\t#retweet_to_tweet_id\t#user_name\t#tweet\t#DATE='+d['DATE']+'\t#SEARCHTOKEN=echtalles\n'
#	print("output.text",len(output.text),output.text[-900:])
	if output.text[:1000] == dumpoutput: #If there isn't any tweet try the request again for 10 times.
		logging.info("There isn't any tweet yet. Starting to request tweets every "+ str(requestwait) +" minutes, maximum "+ str(requestloop) +" times")
		#print("dumpoutput") 
		for i in range(0,requestloop):
			output = False
			while not output:
				time.sleep(60*requestwait) #Wait for the search done at twiqs.nl before the next request
				output = RequestTweets(d)
			if output.text[:1000] == dumpoutput: #If there isn't any tweet again, it will skip this hour.
		#		print("skip hour")
				logging.info('No tweet at ' + str(i))
				#lost_tweets.insert(0,d['DATE'])
				#success = False
			else:
				logging.info('Tweets came on '+ str(i))
		#		print("tweets collected")
				break
	else:
		logging.info('Tweets are O.K.')


	#Check the results one last time if there isn't any tweet send an e-mail;
	if output.text[:1000] == dumpoutput: #If there isn't any tweet again, it will skip this hour.
		logging.warning('Still there is not any tweet! It skipped the tweets at '+ d["DATE"])
		send_mail("Lama Events Warning : There isn't any tweet for this hour from twiqs.nl :" + d["DATE"])
		lost_tweets.insert(0,d['DATE'])
		print("no tweets last attempt")
		success = False

	if success:
		#Event Detection; (refer to Florian Kunneman for any issue)
		EventDicts = ep.detect_events(output.text[:-1],e) # [:-1] = ignoring the last '\n' at the bottom of the file.

		if e:

			logging.info('Event Detection Completed')
			for event in EventDicts:
				event['keylist'] = []
				for m in event['keyterms']:
				#mt = m[0].title() #capitalization
					mt = m[0]
					event['keylist'].append(mt)

			if DeleteFormerEvents:
				lecl.remove({ }) #Delete the old events from database
				#we should check the free space
				logging.info('Former events are deleted from the database')
				new_events = calculations.merge_event_sets(EventDicts)			
			else:
				logging.info('Former events are NOT deleted from the database')
				form_events = []
				for p in lecl.find():
					p['date'] = p['date'].date()                         
					form_events.append(p)
				
				print("form events",len(form_events))
				if len(form_events) > 0:
					merged_events = calculations.merge_event_sets(form_events[:],EventDicts)			
					merged_events = calculations.merge_event_sets([],merged_events)
				else:
					merged_events = calculations.merge_event_sets([],EventDicts)			

				new_events = []
				merge_ids = []
				for c,event in enumerate(merged_events):
					#print(c)
					#print(event)
					try:
						v = lecl.find_one({'_id': event['_id']})
						merge_ids.append(event['_id'])
						v['keylist'] = event['keylist']
						v['score'] = event['score']
						v['tweets'] = event['tweets']
					except KeyError:
						new_events.append(event)
				#new_events = merged_events[len(form_events):]
				#delete merged events
				all_ids = set([x['_id'] for x in form_events])
				bad_ids = list(all_ids - set(merge_ids))
				for bid in bad_ids:
					lecl.remove({'_id' : bid})

			for v in new_events: #For every detected event
					#TimeToEventEstimation Calculations;
					createDate = datetime.now() #TTE Estimation will be added to the current time
					randomTTE = random.uniform(0.0, 193.0) #random number for estimation (for now)
					hh, premm = divmod(randomTTE, 1)
					mm = (60*premm)*0.1
					v['Estimation'] = createDate + timedelta(hours=int(hh), minutes=int(mm))

					#Convert date formats to datetime format;
					#to avoid this error : "bson.errors.InvalidDocument: Cannot encode object: datetime.date(2015, 6, 3)"
					v['date'] = datetime.combine(v['date'], datetime.min.time())

					if DeleteTweetDetails:
						#del v['keyterms']
						for i in v['tweets']:
							del i['date'], i['date references'], i['text'], i['entities']
				
					else:
						#If you don't delete details; convert date formats to datetime format;
						for i in v['tweets']:
							i['date'] = datetime.combine(i['date'], datetime.min.time())

					#Write to database event by event;
					try:			
						lecl.insert(v)
					except:
						print("cant insert, check database", dir(lecl))
						break

                                

			if DeleteTweetDetails:
				logging.info("Tweet Details Deleted")

			logging.info("New Events Written to Database")

#If True, don't contain details of tweets except ids and users. Also don't contain the keyterms of events after keeping them in keylist.
DeleteTweetDetails = False

#If True, delete the former events from mongo db.
DeleteFormerEvents = False

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
	if timereminder == 1:
		logging.info('Waiting for the next hour')

	#Continue waiting if you are in the same hour. Otherwise process the next hour:
	if payload['DATE'] == pDate:
		if len(lost_tweets) > 0:
			payload_lost['DATE'] = lost_tweets.pop()
			event_procedure(payload_lost,e=False)
			#with open("tmp/lostevents.txt","r") as f:
		#		lost_tweets.extend([x.strip() for x in f.readlines()])
		#	lost_tweets = list(set(lost_tweets))
			with open("tmp/lostevents.txt","w") as f: 
				f.write("\n".join(lost_tweets))
				f.close()
	else:
		payload['DATE'] = pDate
		event_procedure(payload)
                
