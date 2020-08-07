#!/bin/bash

set -e

# activate our virtual environment here
. /opt/pysetup/.venv/bin/activate

echo "Starting Development Enviroment"

if [ "$1" = "runserver" ]; then
	python /dev_app/manage.py runserver 0.0.0.0:$PORT
elif [ "$1" = 'manage' ]; then
	python /dev_app/manage.py "${@:2}"
elif [ "$1" = 'lint_mounted_dir' ]; then
	black --config $PYSETUP_PATH/pyproject.toml --check /dev_app
	isort --settings-path $PYSETUP_PATH/pyproject.toml --recursive --check-only /dev_app
else
	exec "$@"
fi

exit
