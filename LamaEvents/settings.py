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
########################## PyMongo insted of MongoEngine 21/06/2018 ####################################
"""
Since MongoEngine stopped supporting Django natively as well after the version 0.9. Consequently. Thus it might be a good idea to make Django - MongoDB connections without MongoEngine, but with PyMongo.
    Instead of MongoEngine, PyMongo could be used to query MongoDB.
    Python functions with PyMongo queries could be written.
    In the models.py, there are small functions to enrich the data with more information. These small functions should be implemented right after    	 the queries to enrich the data in the same way. See the LamaEvents documentation for more information on the functions.
    The data should be returned in the same structure that MongoEngine returns right now. If the structure is kept the same, it will not break the  	flow.
"""
########################## ====================================== #####################################

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
HOSTNAME = os.uname()[1]

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

import getpass

from pymongo import MongoClient
from bson import ObjectId

import configparser

# The passwords and some private configurations encrypted in a different file.
# We are calling the informations from that file with using ConfigParser.
config = configparser.ConfigParser()


if BASE_DIR.startswith('/home'):
    config.read("oauth.ini")
    print("DEBUG set to True")
    DEBUG = True
    TEMPLATE_DEBUG = True
elif HOSTNAME[:9] == "applejack": 
    config.read('/scratch2/www/LamaEvents/oauth.ini')
    DEBUG = False
    TEMPLATE_DEBUG = False
elif HOSTNAME == "mlp01":
    config.read('/var/www/lamaevents/live/repo/oauth.ini')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get('LE_settings', 'secret_key')


ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'lamaevents.cls.ru.nl', 'applejack.science.ru.nl/lamaevents/']


# Application definition;

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

db_name = config.get('LE_script_db', 'db_name')
db_host = config.get('LE_script_db', 'client_host')
db_port = int(config.get('LE_script_db', 'client_port'))

LAMAEVENT_COLL = MongoClient(db_host, db_port)[db_name]['lecl']

# Internationalization;

LANGUAGE_CODE = 'nl'

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

USE_L10N = True

USE_TZ = True

URLPREFIX = ''

# Static files;

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
