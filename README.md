RC-STATS V2
===================


Fresh Install
-------------
Using virtualenv for the project.
```
python3 -m venv --without-pip rcstats
cd rcstats
source bin/activate
```
> Reference - I followed this for Ubuntu 10.04, hopefully the newer version doesn't have this problem.
http://askubuntu.com/questions/488529/pyvenv-3-4-error-returned-non-zero-exit-status-1
http://askubuntu.com/questions/279959/how-to-create-a-virtualenv-with-python3-3-in-ubuntu

Retrieve the project from git and install requirements.
```
clone git@github.com:AnthonyHonstain/rcstatsV2.git
cd rcstatsV2
pip install -r reqs/dev.txt
```

Install initial SQL Data (sync db first)
```
python manage.py loaddata core/fixture/ClassNames.json
// FOR HEROKU
heroku run python manage.py loaddata core/fixture/ClassNames.json
```


Dev Cheat Sheet
-------------
Run the unit test suite.
```
python manage.py test
```
Basic dev tasks.
```
// Run the dev env so it can be accessed while developing in VM.
python manage.py runserver 0.0.0.0:8000

// Resetting DB for testing
python manage.py migrate uploadresults 0001_initial
python manage.py makemigrations 
python manage.py migrate
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
* underscore http://underscorejs.org/
* moment http://momentjs.com/docs/
