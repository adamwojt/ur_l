#!/bin/bash

set -e
Cyan='\e[36m'
Red='\e[31m'

# activate our virtual environment here
. /opt/pysetup/.venv/bin/activate

printf $Red"*******************************\n"
printf $Red"*******************************\n"
printf $Red"Starting Production Enviroment\n"
printf $Red"*******************************\n"
printf $Red"*******************************\n"

if [ "$1" = "runserver" ]; then
	printf $Cyan"Port -> $UR_L_PORT\n"
	printf $Cyan"Workers -> $NUM_GUNICORN_WORKERS\n"
	printf $Cyan"Use Cache -> $URL_USE_CACHE\n"
	printf $Cyan"Cache timeout on create -> $CACHE_TIMEOUT_CREATE\n"
	printf $Cyan"Cache timeout on read -> $CACHE_TIMEOUT_READ\n"
	printf $Cyan"Log Token Collision -> $LOG_TOKEN_COLLISION\n"

	# This is just to make `docker-compose up` work first time
	# Real production should not run these two below
	python manage.py collectstatic --no-input
	python manage.py migrate --no-input

	gunicorn --bind 0.0.0.0:$UR_L_PORT --workers $NUM_GUNICORN_WORKERS --capture-output ur_l.wsgi:application
elif [ "$1" = 'manage' ]; then
	python manage.py "${@:2}"
elif [ "$1" = 'test' ]; then
	pytest --cov=. --cov-fail-under=$COV_FAIL_THRESHOLD
else
	exec "$@"
fi

exit
