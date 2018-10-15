#!/bin/bash

ROOTDIR=/var/www/lamaevents/live/repo/

. /var/www/lamaevents/live/le_env/bin/activate

#python3 manage.py runserver 8860
uwsgi --plugin python3 --virtualenv $VIRTUAL_ENV --socket 127.0.0.1:8860 --chdir $ROOTDIR --wsgi-file $ROOTDIR/LamaEvents/wsgi.py --logto $ROOTDIR/lamaevents.uwsgi.log --log-date --log-5xx --master --processes 4 --threads 2 --need-app
