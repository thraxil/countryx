#!/bin/bash

cd /var/www/countryx/countryx/
python manage.py migrate --noinput --settings=countryx.settings_docker
python manage.py collectstatic --noinput --settings=countryx.settings_docker
python manage.py compress --settings=countryx.settings_docker
gunicorn --env \
  DJANGO_SETTINGS_MODULE=countryx.settings_docker \
  countryx.wsgi:application -b 0.0.0.0:8000 -w 3 \
  --access-logfile=- --error-logfile=-
