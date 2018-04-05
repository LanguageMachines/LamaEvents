"""

All loggings are written to 'LamaEvents.log'
You can see the last loggings with this command line code::

	>> tail -F Lamaevents.log 
5B
"""

import sys
import smtplib
import pymongo
import logging
import configparser
import json
from bson.objectid import ObjectId
import re
import datetime

eventfile = sys.argv[1]
eventout = sys.argv[2]

#Logging Configurations;
logging.basicConfig(
		format='%(asctime)s, %(levelname)s: %(message)s',
		filename='LamaEvents.log',
		datefmt='%d-%m-%Y, %H:%M',
		level=logging.INFO)

logging.info('Lama Events Script Started')

#Get all the private configurations;
config = configparser.ConfigParser()
config.read('/scratch2/www/LamaEvents/oauth.ini')

#MongoLab OAuth;
client_host = config.get('LE_script_db', 'client_host')
client_port = int(config.get('LE_script_db', 'client_port'))
db_name = config.get('LE_script_db', 'db_name')
#user_name = config.get('LE_script_db', 'user_name')
#passwd = config.get('LE_script_db', 'passwd')

def return_datetime(datestr,timestr):
        parse_date = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
        date = parse_date.search(datestr).groups(1)
        parse_time = re.compile(r"^(\d{2}):(\d{2})")
        timeparse = parse_time.search(timestr).groups(1)
        datetime_obj = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),int(timeparse[0]),0,0)    
        return datetime_obj

def import_datetime(datetime):
        date,time = datetime.split()
        dt = return_datetime(date,time)
        return dt

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

print('Connecting to database')
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

print('Reading in events')
# read in events
with open(eventfile, 'r', encoding = 'utf-8') as file_in:
        eventdicts = json.loads(file_in.read())

# convert events to lama events
lamadicts = []
merge_ids = []
try:
	all_ids = set([event['_id'] for event in lecl.find()])
except:
	all_ids = []
print('Adding events, current number of events in database:',len(all_ids)) 

for eventdict in eventdicts:
#      	print(eventdict['mongo_id'])
	if 'mongo_id' in eventdict.keys():
       		if eventdict['mongo_id'] != False: # already in database
               		print('In DB')
#                lecl.insert({'_id': ObjectId(eventdict['mongo_id'])})
               		event = lecl.find_one({'_id': ObjectId(eventdict['mongo_id'])})
               		merge_ids.append(event['_id']) 
               		for key in ['entities','location','cycle','predicted','periodicity','eventtype']:
                       		event[key] = eventdict[key]
#               lecl.update({"_id" :ObjectId(eventdict['mongo_id']) },{"cycle":eventdict['cycle'], "predicted":eventdict['predicted'], "periodicity":eventdict['periodicity'], "eventtype":eventdict['eventtype']})
               		event['score'] = float(eventdict['score'])
               		event['tweets'] = [{'id':t['id'], 'user':t['user']} for t in eventdict['tweets']]
               		event['date'] = import_datetime(eventdict['datetime']).replace(hour=0,minute=0,second=0)
               		lecl.save(event)
               		lamadicts.append(eventdict)
        	else:
                	new_event = {}
                	new_eventdict = {}
                	for key in ['entities','location','cycle','eventtype','predicted','periodicity']:
                        	new_event[key] = eventdict[key]
                	new_event['score'] = float(eventdict['score'])
                	new_event['tweets'] = [{'id':t['id'], 'user':t['user']} for t in eventdict['tweets']]
                	new_event['date'] = import_datetime(eventdict['datetime']).replace(hour=0,minute=0,second=0)
                	mongo_id = lecl.insert(new_event)
                	new_eventdict = eventdict
                	new_eventdict['mongo_id'] = str(mongo_id)
                	merge_ids.append(mongo_id)
                	lamadicts.append(new_eventdict)
	else:
               	new_event = {}
               	new_eventdict = {}
               	for key in eventdict.keys():
                       	new_event[key] = eventdict[key]
               	new_event['score'] = float(eventdict['score'])
               	new_event['tweets'] = [{'id':t['id'], 'user':t['user']} for t in eventdict['tweets']]
               	new_event['date'] = import_datetime(eventdict['datetime']).replace(hour=0,minute=0,second=0)
               	mongo_id = lecl.insert(new_event)
               	new_eventdict = eventdict
               	new_eventdict['mongo_id'] = str(mongo_id)
               	merge_ids.append(mongo_id)
               	lamadicts.append(new_eventdict)

# delete merged events
bad_ids = list(all_ids - set(merge_ids))
print('num bad ids',len(bad_ids))
for bid in bad_ids:
        lecl.remove({'_id' : bid})
print('Done. New number of events in database:',len(merge_ids))

# write events
for ld in lamadicts:
        if not isinstance(ld['mongo_id'], str):
                print('NO str',ld)
with open(eventout,'w',encoding='utf-8') as file_out:
        json.dump(lamadicts,file_out)
