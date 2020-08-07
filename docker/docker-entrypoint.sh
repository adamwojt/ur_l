#!/bin/bash

set -e

# activate our virtual environment here
. /opt/pysetup/.venv/bin/activate

echo "Starting Production Enviroment"

if [ "$1" = "runserver" ]; then
	gunicorn --bind 0.0.0.0:$PORT ur_l.wsgi:application
elif [ "$1" = 'manage' ]; then
	python manage.py "${@:2}"
fi

exit
