import requests

import pymongo
from pymongo import MongoClient

import time
import datetime as datetime

import DEvents.event_pairs as event_pairs

#MongoLab Connection;
connection = MongoClient(XXX)
ledb = connection["XXX"]
ledb.authenticate("XXX", "XXX")
lecl = ledb.lecl

ep = event_pairs.Event_pairs()

payload = {'SEARCH': 'echtalles', 'DATE': 'start', 'DOWNLOAD':True, 'SHOWTWEETS':True}

while True:
    time.sleep(300)
    a = datetime.datetime.now().strftime("20%y%m%d%H")
    b = datetime.datetime.now().strftime("%H%M")
    nowDATE = a+'-'+a
    if payload['DATE'] == nowDATE:
        print(b)
        continue
    else:
        payload['DATE'] = nowDATE
        print('***'+payload['DATE'])
        #Request to Twiqs;
        output = requests.get("http://145.100.57.182/cgi-bin/twitter", params=payload, cookies={'cookie':'XXX'})
    #Add an automatic cookie finder here (requests.Session())
        print("***Request Done.")
        #Event Detection;
        EventDic = ep.detect_events(output.text[:-1]) # [:-1] = ignoring the last '\n' at the bottom of the file.
        #Date to Datetime;
        for k,v in EventDic.items():
            v['date'] = datetime.datetime.combine(v['date'], datetime.datetime.min.time())
            for i in v['tweets']:
                i['date'] = datetime.datetime.combine(i['date'], datetime.datetime.min.time())
            lecl.insert(v) #Writing to Database
    #Add here some break for  too long processes
        continue
