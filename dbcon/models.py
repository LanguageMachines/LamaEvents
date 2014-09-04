"""
This file has the database definitions. 
Since we used MongoDB for database; there isn't any need to do migration or synch after the changes unlikely sqlite.

You can call the functions you wrote here, in template like 'event.timeLeft'.
"""

from django.db import models

from datetime import datetime, timedelta

from mongoengine import * #Document and EmbeddedDocument classes come from here.

class Tweets(EmbeddedDocument):
	user = StringField()
	id = StringField()


class Events(Document):
	"""It represents MongoDB structure. It inherits the Document Class from mongoengine"""
	meta = {'collection' : 'lecl'}
	tweets = ListField(EmbeddedDocumentField(Tweets))
	date = DateTimeField()
	score = FloatField()
	Estimation = DateTimeField()
	keylist = ListField(StringField())	

	def linkDate(self):
		"""Creates dates which can be used in links to exact date. Especially for EventDetail to EventsofDate"""
		ld = self.date.strftime("%d-%m-%Y") #dates which can be used in links
		return ld

	def datestr(self):
		"""
		Only defines a format to show in templates
		It needed because we are using date field as datetime normally.
		"""
		ds = self.date.strftime("%d %B %Y %A")#to string format
		return ds

	def Estimationstr(self):
		"""Only defines a format to show in templates"""
		es = self.Estimation.strftime("%d %B %Y - %H:%M")#to string format
		return es

	def timeLeft(self):
		"""Calculates the time left to the event."""
		if self.Estimation > datetime.now():
			hl =  self.Estimation - datetime.now()
			#!IDEA!: add 'time left' string to hl.
		else:
			hl = "Het event is al geweest."
		return hl








