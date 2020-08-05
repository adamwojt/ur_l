#!/bin/sh

set -e

# activate our virtual environment here
. /opt/pysetup/.venv/bin/activate
cd ./app
if [ "$1" = 'runserver' ]; then
	gunicorn --bind 0.0.0.0:$PORT ur_l.wsgi:application
elif [ "$1" = 'migrate' ]; then
	python manage.py migrate
elif [ "$1" = 'lint_mounted_dir' ]; then
	if [ "$TARGET_ENV" != 'development' ]; then
		echo "Only in development target, perhaps change TARGET_ENV and build again."
		exit
		fi
	black --config $PYSETUP_PATH/pyproject.toml --check /dev_app
	isort --settings-path $PYSETUP_PATH/pyproject.toml --recursive --check-only /dev_app
fi

exit
