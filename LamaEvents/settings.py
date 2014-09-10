"""
Django settings for LamaEvents project.

The only thing different than normal here is we used MongoDB instead of any relational database.
Also we used MongoEngine to make the connection between Django and MongoDB.

The configurations of this special case is the following code::

	DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.dummy',
	    },
	}
	
	AUTHENTICATION_BACKENDS = (
	    'mongoengine.django.auth.MongoEngineBackend',
	)
	
	SESSION_ENGINE = 'mongoengine.django.sessions'
	SESSION_SERIALIZER = 'mongoengine.django.sessions.BSONSerializer'


	AUTH_USER_MODEL = 'mongo_auth.MongoUser'
	MONGOENGINE_USER_DOCUMENT = 'mongoengine.django.auth.User'

	connect(db_name, host=db_host)

Also, notice we used an if statement to check if the codes are working on Applejack server. 
On the Applejack we have to add 'lamaevents' before all the links we used. Here we are defining it::

	elif HOSTNAME[:9] == "applejack":	#for the server side
		STATIC_URL = '/lamaevents/static/'
		URLPREFIX = '/lamaevents'

.. note:: You can see how we used URLPREFIX in views.py and in the templates.

"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

HOSTNAME = os.uname()[1]

import getpass

from mongoengine import *

import configparser

#The passwords and some private configurations encrypted in a different file.
#We are calling the informations from that file with using ConfigParser.
config = configparser.ConfigParser() 

#Calls the authentication file;
if getpass.getuser() == "ebasar":	#to work on applejack home
	config.read("/home/ebasar/oauth.ini")
	DEBUG = True
	TEMPLATE_DEBUG = True
elif HOSTNAME[:9] == "applejack":	#to work on the server
	config.read('/scratch2/www/LamaEvents/oauth.ini')
	DEBUG = False
	TEMPLATE_DEBUG = False


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get('LE_settings', 'secret_key')


ALLOWED_HOSTS = ['localhost', '127.0.0.1']



# Application definition;

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mongoengine.django.mongo_auth',
    'dbcon',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'LamaEvents.middleware.MobileDetectionMiddleware',
)

ROOT_URLCONF = 'LamaEvents.urls'

WSGI_APPLICATION = 'LamaEvents.wsgi.application'


# Database;
#We used MongoDB as database instead of sqlite or any other relational database. 
#So configuration is little bit different;

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy',
    },
}

AUTHENTICATION_BACKENDS = (
    'mongoengine.django.auth.MongoEngineBackend',
)

SESSION_ENGINE = 'mongoengine.django.sessions'
SESSION_SERIALIZER = 'mongoengine.django.sessions.BSONSerializer'


AUTH_USER_MODEL = 'mongo_auth.MongoUser'
MONGOENGINE_USER_DOCUMENT = 'mongoengine.django.auth.User'


db_name = config.get('LE_settings', 'db_name')
db_host = config.get('LE_settings', 'db_host')


#This code is connet to MongoDB host. The host now is MongoLab;
connect(db_name, host=db_host)


# Internationalization;

LANGUAGE_CODE = 'nl'

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files;

if getpass.getuser() =='ebasar':	#to work on applejack home
	STATIC_URL = '/static/'
	URLPREFIX = ''
elif HOSTNAME[:9] == "applejack":	#for the server side
	STATIC_URL = '/lamaevents/static/'
	URLPREFIX = '/lamaevents'
else:								#to work on local
	STATIC_URL = '/static/'
	URLPREFIX = ''


STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
)








