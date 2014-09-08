How to run
============

Python version 3.4
Django version 1.6
MongoEngine 



Django Project
----------------

	Running the Django app;

		- Go to the project folder which contains manage.py; currently Hede
			>> python manage.py runserver (deafult port 8000)
		- You can provide another port, for example 4545;
			>> python manage.py runserver 4545
	

	Model-View-Controller
	
		- Main folder of this project is <project_folder>/Lamaevents
		- It uses views.py from dbcon folder, urls.py from LamaEvents folder

LamaEvents Script
-----------------

	- Go to the project folder which contains DEvents, ADNEXT, coco_out, tmp, pynlpl etc.
		>> python LamaEvents.py



Python Paths
-------------

Event Detection::

	export PYTHONPATH=/vol/customopt/uvt-ru/src/colibri/scripts:/vol/customopt/uvt-ru/lib/python3.2/site-packages:~/Projects/ADNEXT/

Anaconda::

	export PYTHONPATH="~/Anaconda3/lib/python3.4/site-packages:$PYTHONPATH"
	export PATH="~/Anaconda3/bin/:$PATH"




