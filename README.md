# UR_L shortener

### Requirements

- [Docker >= 17.05](https://www.docker.com/)
- [docker-compose >= 1.21.0](https://docs.docker.com/compose/)
- [Python >= 3.8](https://www.python.org/downloads/release/python-381/)
- [Poetry](https://github.com/python-poetry/poetry)

---
**NOTE** - Run all commands from the project root

## Configuration

Most of configuration is done via Environment variables that are passed to `docker-compose` [(docs)](https://docs.docker.com/compose/environment-variables/). 
You can either set them up in your shell or create `.env` in project root.
See [.env.template file](.env.template) for possible options and defaults.

**NOTE** - Set at least:

		DJANGO_SECRET_KEY
		TARGET_ENV (development|production)

---

## Local development

With `TARGET_ENV=development` -> `docker-compose up`. Access in browser -> `localhost:8001`
This loads [docker-compose.override.yml](docker-compose.override.yml) and mounts app directory to container.
Any code changes will restart server dynamically.

### Commands:
- Run development server - `docker-compose up`
- Run development server (with stdout for debug) -  `docker-compose run -p 8001:8001 ur_l`
- To run local dir tests - `docker-compose run ur_l test`
- To run local dir linter `docker-compose run ur_l lint_mounted_dir`
- Access to manage.py - `docker-compose run manage {args}`

**NOTES**:
- First run will need `docker-compose run ur_l manage migrate`
- Nginx is not running in dev but it's port (`8000`) is reserved.
- Redis cache is dev should be persistent - to disable, remove redis volume in [docker-compose.override.yml](docker-compose.override.yml)

---

## Production

With `TARGET_ENV=production` -> `docker-compose -f docker-compose.yml up`. Access in browser -> `localhost:8000`
Local code changes will not be visible.

### Commands:
- Run server - `docker-compose -f docker-compose.yml up`
- To run tests - `docker-compose -f docker-compose.yml run ur_l test`
- Access to manage.py - `docker-compose -f docker-compose.yml run ur_l manage {args}`

**NOTES**:
- Local code changes will not be visible after image is built.

---

## Poetry


If any changes to dependencies, run below before rebuilding docker images:

        poetry update

See the [poetry docs](https://python-poetry.org/docs/) for information on how to add/update dependencies.

---

## Docker

The Dockerfile uses multi-stage builds to run lint before building the production stage. If linting fails the build will fail too.

### Linters that run on build:
- [isort](https://pypi.org/project/isort/) -> config [here](.pyproject.yml)
- [black](https://github.com/psf/black) -> config [here](.pyproject.yml)
- [safety](https://pypi.org/project/safety/)

Same commands as in [Dockerfile](Dockerfile) can be run in `poetry shell`

**NOTES**:
- To rebuild images, run `docker-compose build`
- [.pyproject.yml](.pyproject.yml) and [poetry.lock](poetry.lock) are used for dependency caching

---
