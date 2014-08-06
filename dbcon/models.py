from django.db import models

from mongoengine import *

class Tweets(EmbeddedDocument):
	date_references = StringField()
	entities = StringField()
	user = StringField()
	id = StringField()
	text = StringField() 
	date = StringField()


class Events(Document):
	meta = {'collection' : 'lecl'}
	keyterms = ListField(default=lambda: [1,2,3])
	tweets = ListField(EmbeddedDocumentField(Tweets))
	date = StringField()
	score = FloatField()

