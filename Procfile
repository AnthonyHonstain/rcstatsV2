web: newrelic-admin run-program gunicorn rcstatsV2.wsgi --timeout 30 --log-file -
scheduler: python manage.py celery worker -B -E --maxtasksperchild=1000
