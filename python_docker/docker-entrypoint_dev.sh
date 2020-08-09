#!/bin/bash
set -e
Green='\e[32m'
PYTEST_CACHE_DIR=.pytest_cache

/wait-for-postgres.sh

# activate our virtual environment here
. /opt/pysetup/.venv/bin/activate

printf $Green"*******************************\n"
printf $Green"Starting Development Enviroment\n"
printf $Green"*******************************\n"

if [ "$1" = "runserver" ]; then
	python manage.py runserver 0.0.0.0:$UR_L_PORT
elif [ "$1" = 'manage' ]; then
	python manage.py "${@:2}"
elif [ "$1" = 'lint_mounted_dir' ]; then
	black --config $PYSETUP_PATH/pyproject.toml --check .
	isort -sg migrations --settings-path $PYSETUP_PATH/pyproject.toml --recursive --check-only .
elif [ "$1" = 'test' ]; then
	if [ -d "$PYTEST_CACHE_DIR" ]; then rm -Rf $PYTEST_CACHE_DIR; fi
	pytest --cov-config=.coveragerc --cov-fail-under=$COV_FAIL_THRESHOLD --cov=. .
else
	exec "$@"
fi

exit
