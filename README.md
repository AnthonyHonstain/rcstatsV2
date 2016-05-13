RC-STATS V2
===================


Fresh Install
-------------
Dependencies (installed with Synaptic on ubuntu 15.04
* python3 (already installed)
* virtualenv and python3-virtualenv
* postgresql
 * Create a new postgresql user (I called it pgadmin) - "sudo -i -u postgres" and "createuser -P -s -e pgadmin"
 * Adjust auth method for dev db (add one for your new user) and restart - http://stackoverflow.com/questions/18664074/getting-error-peer-authentication-failed-for-user-postgres-when-trying-to-ge
 * Add the rcstats DB "createdb -U pgadmin -W rcstatsV2"
* celery - TODO
* redis - defined in the configs, but its going to expect localhost:6379
 * Great guide - http://redis.io/topics/quickstart

Notable Third Party Dependencies
* http://getbootstrap.com/getting-started/
* http://bootstrap-table.wenzhixin.net.cn/getting-started/
* http://www.bootstrap-switch.org/

Using virtualenv for the project.
```
virtualenv -p /usr/bin/python3 rcstats
cd rcstats
source bin/activate
```
> ~~Reference - I followed this for Ubuntu 10.04, hopefully the newer version doesn't have this problem.
http://askubuntu.com/questions/488529/pyvenv-3-4-error-returned-non-zero-exit-status-1
http://askubuntu.com/questions/279959/how-to-create-a-virtualenv-with-python3-3-in-ubuntu~~

Retrieve the project from git and install requirements.
```
git clone git@github.com:AnthonyHonstain/rcstatsV2.git
cd rcstatsV2
pip install -r reqs/dev.txt
```

Configure your dev settings
* "cp rcstatsV2/settings/settings_secret.py_TEMPLATE rcstatsV2/settings/settings_secret.py"
* Add your local database and set a secret key (leave the email accounts null for now).

Install initial SQL Data (sync db first)
```
python manage.py syncdb
python manage.py loaddata core/fixture/ClassNames.json
// Create a starter track so you can see the landing page
python manage.py loaddata core/fixture/TrackName.json

// FOR HEROKU
heroku run python manage.py loaddata core/fixture/ClassNames.json

// Should pass tests at this stage
python manage.py test
```

Create an admin user so we can get the site running locally
* "python manage.py createsuperuser"
* "python manage.py runserver 0.0.0.0:8000"
* Login to http://localhost:8000/admin/
 * Home -> Sites -> Sites -> Add site
  * Domain name: 127.0.0.1:8000
  * Display name: rc-stats.com
 * Delete the example site 
* Connect and load a race using the web uploader - http://localhost:8000/upload/easyupload_track/
 * Sample races are included in the repository - rcstatsV2/samplerace/
* Now that you have a race in the system - navigate to http://localhost:8000/
 * Navigate around - http://localhost:8000/results/singleracedetail/1/ 

Dev Cheat Sheet
-------------
Run the unit test suite - AUTOMATED tests should cover a large portion of the backend functionality.
```
python manage.py test
```

Basic dev tasks.
```
// Run the dev env so it can be accessed while developing in VM.
python manage.py runserver 0.0.0.0:8000
// Start Celery running - best to use a seperate terminal. 
//    Even with concurrency 1, you will still see three processes for celery.
python manage.py celeryd -E -B --loglevel=INFO --concurrency 1
// Can use IPython notebook to run commands.
python manage.py shell_plus --notebook

// Resetting DB for testing
python manage.py migrate uploadresults 0001_initial
python manage.py makemigrations 
python manage.py migrate
```
Important dev links -
* http://127.0.0.1:8000/admin/  Django admin site
* http://127.0.0.1:8000/  Site root

Deployment
```
// Remeber to deploy database changes.
heroku run python manage.py migrate
```


Project Structure
-------------
Python3 site using Django1.7

rcstatsV2
* settings, shared templates, and urls for the whole project.

core
* The most important models (the race results).
* This also contains root of the site. 

uploadresults
* UI uploader and API uploader, responsible for ingesting races into the system.

important third party apps
* Userena 1.4
* Django Rest Framework 3

javascript and css
* jquery (required for bootstrap)
* bootstrap http://getbootstrap.com/getting-started/
* bootstrap-table http://bootstrap-table.wenzhixin.net.cn/getting-started/
* boostrap-swtich http://www.bootstrap-switch.org/
* underscore http://underscorejs.org/
* moment http://momentjs.com/docs/


Deployment
-------------
Deployed and hosted using Heroku

Currently (4/18) set to use a single heroku web dyno (even though we have both a web client and a celery worker).
* Watch out for celery concurrency which can create to many workers and take all the memory on the dyno.
* Honcho to start additional process http://www.radekdostal.com/content/heroku-running-multiple-python-processes-single-dyno-using-honcho

Monitoring
Heroku System Logs - a really good guide https://devcenter.heroku.com/articles/logging
```
heroku logs -t -s heroku
```
Application Logs - Need to update app name
```
heroku logs -t -s nameless-ridge-5720
```

Architecture
-------------
* Static files
** I am currently using gunicorn to host my statics directly on heroku, this not ideal. But it easy to understand and develop against (for a site with very low traffic) https://github.com/kennethreitz/dj-static https://github.com/rmohr/static3
** In the future - this would be a better approach - https://devcenter.heroku.com/articles/s3
