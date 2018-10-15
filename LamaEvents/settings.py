"""
Since MongoEngine stopped supporting Django natively as well after the version 0.9. So we make Django - MongoDB connections with PyMongo.
    Instead of MongoEngine, PyMongo used to query MongoDB.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
HOSTNAME = os.uname()[1]

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

print(BASE_DIR)

import getpass

from pymongo import MongoClient
from bson import ObjectId

import configparser

# The passwords and some private configurations encrypted in a different file.
# We are calling the informations from that file with using ConfigParser.
config = configparser.ConfigParser()


if BASE_DIR.startswith('/home'):
    config.read("/home/gghanem/LamaEvents/oauth.ini")
    print("DEBUG set to True")
    DEBUG = True
    TEMPLATE_DEBUG = True
elif HOSTNAME[:9] == "applejack":
    config.read('/var/www/lamaevents/live/repo/oauth.ini')
    DEBUG = True
    TEMPLATE_DEBUG = True
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
