#!/bin/bash

set -e
Green='\e[32m'

# activate our virtual environment here
. /opt/pysetup/.venv/bin/activate

printf $Green"*******************************\n"
printf $Green"Starting Development Enviroment\n"
printf $Green"*******************************\n"

if [ "$1" = "runserver" ]; then
	python /dev_app/manage.py runserver 0.0.0.0:$UR_L_PORT
elif [ "$1" = 'manage' ]; then
	python /dev_app/manage.py "${@:2}"
elif [ "$1" = 'lint_mounted_dir' ]; then
	black --config $PYSETUP_PATH/pyproject.toml --check /dev_app
	isort -sg migrations --settings-path $PYSETUP_PATH/pyproject.toml --recursive --check-only /dev_app
elif [ "$1" = 'test' ]; then
	pytest --cov-config=/dev_app/.coveragerc --cov-fail-under=$COV_FAIL_THRESHOLD --cov=/dev_app /dev_app
else
	exec "$@"
fi

exit
