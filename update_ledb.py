"""

All loggings are written to 'LamaEvents.log'
You can see the last loggings with this command line code::

	>> tail -F Lamaevents.log 

"""

import sys
import smtplib
import pymongo
import logging
import configparser
import json
from bson.objectid import ObjectId

from dte.functions import time_functions

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
config.read('/scratch/fkunneman/lamaevents/oauth.ini')

#MongoLab OAuth;
client_host = config.get('LE_script_db', 'client_host')
client_port = int(config.get('LE_script_db', 'client_port'))
db_name = config.get('LE_script_db', 'db_name')
#user_name = config.get('LE_script_db', 'user_name')
#passwd = config.get('LE_script_db', 'passwd')

def import_datetime(datetime):
        date,time = datetime.split()
        dt = time_functions.return_datetime(date,time,minute=True,setting='vs')
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
all_ids = set([event['_id'] for event in lecl.find()])
print('Adding events, current number of events in database:',len(all_ids)) 

for eventdict in eventdicts:
        if 'mongo_id' in eventdict.keys(): # existing event
                print('mongo id in')
                event = lecl.find_one({'_id': ObjectId(event['mongo_id'])})
                merge_ids.append(event['_id']) 
                for key in ['entities','location']:
                        event[key] = eventdict[key]
                event['score'] = float(eventdict['score'])
                event['tweets'] = [{'id':t['id'], 'user':t['user']} for t in eventdict['tweets']]
                event['date'] = import_datetime(eventdict['datetime']).replace(hour=0,minute=0,second=0)
                lamadicts.append(eventdict)
        else:
                new_event = {}
                new_eventdict = {}
                for key in ['entities','location']:
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
