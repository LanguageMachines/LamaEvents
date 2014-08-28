from django.db import models

from datetime import datetime, timedelta

from mongoengine import *

class Tweets(EmbeddedDocument):
	user = StringField()
	id = StringField()


class Events(Document):
	meta = {'collection' : 'lecl'}
	tweets = ListField(EmbeddedDocumentField(Tweets))
	date = DateTimeField()
	score = FloatField()
	Estimation = DateTimeField()
	keylist = ListField(StringField())	

	def datestr(self):
		ds = self.date.strftime("%d %B 20%y %A")#to string format
		return ds

	def Estimationstr(self):
		es = self.Estimation.strftime("%d %B 20%y - %H:%M")#to string format
		return es

	def timeLeft(self):
		if self.Estimation > datetime.now():
			hl = self.Estimation - datetime.now()
		else:
			hl = "Event is in the past"
		return hl

	def keylistwc(self):
		keylistwc = []
		keylistwc = ", ".join(self.keylist) #adding comma
		return keylistwc







