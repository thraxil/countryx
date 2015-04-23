#!/bin/bash

cd /var/www/countryx/countryx/
python manage.py migrate --settings=countryx.settings_docker
gunicorn --env \
  DJANGO_SETTINGS_MODULE=countryx.settings_docker \
  countryx.wsgi:application -b 0.0.0.0:8000 -w 3
