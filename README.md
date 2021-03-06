![CI](https://github.com/adamwojt/ur_l/workflows/Docker/badge.svg?branch=master&event=push)![Bandit](https://github.com/adamwojt/ur_l/workflows/Bandit%20Security/badge.svg?branch=master&event=push)

[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://timothycrosley.github.io/isort/)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![Coverage](https://img.shields.io/badge/coverage-90%25%2B-brightgreen)](https://github.com/adamwojt/ur_l/actions)[![Safety](https://img.shields.io/badge/%20pyupio%20-safety-blue)](https://github.com/pyupio/safety)

# UR_L shortener

### Requirements

- [![Docker >= 17.05](https://img.shields.io/badge/%20docker-%3E%3D%2017.05-blue)](https://www.docker.com/)
- [![docker-compose >= 1.21.0](https://img.shields.io/badge/%20docker--compose-%3E%3D%201.21.0-blue)](https://docs.docker.com/compose/)
- [![Python >= 3.8](https://img.shields.io/badge/python-%3E%3D%203.8-blue)](https://www.python.org/downloads/release/python-381/)
- [![Poetry](https://img.shields.io/badge/poetry-1.0.10-blue)](https://github.com/python-poetry/poetry)

---
**NOTE** - Run all commands from the project root

## Configuration

Most of the configuration is done via Environment variables that are passed to `docker-compose` [(docs)](https://docs.docker.com/compose/environment-variables/). 
You can either set them up in your shell or create `.env` in project root.
See [.env.template file](.env.template) for possible options and defaults.

**NOTE** - Set at least:

		DJANGO_SECRET_KEY
		TARGET_ENV (development|production)

---
## API
Interactive docs are available under `/api/docs`

**how it works**

Once Url is created (via api or admin) - it will redirect permanently from `/{token}` path to original `long_url`.
URL can stay in high demand as backend will constantly refresh Redis cache to `CACHE_TIMEOUT_READ` settings.
Cache is set at create too with `CACHE_TIMEOUT_READ` setting. Cache is updated/deleted on PUT or DELETE. 


**list**
```
GET /api/urls/
Auth method: Basic

Return a list of all the existing urls.
Query Parameters

The following parameters should be included as part of a URL query string.

page	A page number within the paginated result set.
```

**create**
```
POST /api/urls/
Auth method: None (Public)

Create a new short url.
Request Body

The request body should be a "application/json" encoded object, containing the following items.
long_url (required)
click_limit (optional, if set url is deleted after limit is reached)
```

**read**
```
GET /api/urls/{token}/
Auth method: None (Public)


Return the given url using token.
Path Parameters

The following parameters should be included in the URL path.
token required
```
**update**
```
PUT /api/urls/{token}/
Auth method: Basic

Update long url (long_url body needed)

The following parameters should be included in the URL path.
token (required)

The request body should be a "application/json" encoded object, containing the following items.
long_url (required)
click_limit
```
**delete**
```
DELETE /api/urls/{token}/
Auth method: Basic

Delete url and clear cache

The following parameters should be included in the URL path.
token (required)
```

**admin**
There is admin panel available too under `/admin`. Make sure to `createsuperuser` before.

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
- [isort](https://pypi.org/project/isort/) -> config [here](pyproject.yml)
- [black](https://github.com/psf/black) -> config [here](pyproject.yml)
- [safety](https://pypi.org/project/safety/)

Same commands as in [Dockerfile](Dockerfile) can be run in `poetry shell`

**NOTES**:
- To rebuild images, run `docker-compose build`
- [pyproject.yml](pyproject.yml) and [poetry.lock](poetry.lock) are used for dependency caching

---

## Benchmarks

To run, execute below with whole stack running:
```docker exec `docker ps -qf "name=ur_l_nginx"` benchmark```

**Fetching url** - Mean time **4.004** ms:

```
Server Software:        nginx/1.18.0
Server Hostname:        localhost
Server Port:            80

Document Path:          /Lq9uJfc

Concurrency Level:      10
Time taken for tests:   20.020 seconds
Complete requests:      5000
Failed requests:        0
Non-2xx responses:      5000
Keep-Alive requests:    4954
Total transferred:      2034770 bytes
HTML transferred:       0 bytes
Requests per second:    249.75 [#/sec] (mean)
Time per request:       40.040 [ms] (mean)
Time per request:       4.004 [ms] (mean, across all concurrent requests)
Transfer rate:          99.25 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:    11   40   8.5     39     243
Waiting:       11   40   8.5     39     243
Total:         11   40   8.5     39     244

Percentage of the requests served within a certain time (ms)
  50%     39
  66%     41
  75%     42
  80%     43
  90%     47
  95%     52
  98%     60
  99%     71
 100%    244 (longest request)

```

**Creating url** - Mean time **3.987** ms:

```
Server Software:        nginx/1.18.0
Server Hostname:        localhost
Server Port:            80

Document Path:          /api/urls/
Document Length:        102 bytes

Concurrency Level:      10
Time taken for tests:   19.935 seconds
Complete requests:      5000
Failed requests:        0
Total transferred:      1990000 bytes
Total body sent:        845000
HTML transferred:       510000 bytes
Requests per second:    250.81 [#/sec] (mean)
Time per request:       39.871 [ms] (mean)
Time per request:       3.987 [ms] (mean, across all concurrent requests)
Transfer rate:          97.48 [Kbytes/sec] received
                        41.39 kb/s sent
                        138.88 kb/s total

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.1      0       3
Processing:    10   40   5.8     39     160
Waiting:       10   39   5.8     39     160
Total:         11   40   5.9     39     160

Percentage of the requests served within a certain time (ms)
  50%     39
  66%     41
  75%     42
  80%     43
  90%     46
  95%     49
  98%     53
  99%     57
 100%    160 (longest request)
```

## CI

![CI](https://github.com/adamwojt/ur_l/workflows/Docker/badge.svg?branch=master&event=push)![Bandit](https://github.com/adamwojt/ur_l/workflows/Bandit%20Security/badge.svg?branch=master&event=push)


### Current workflow

- Build Docker Image (includes [![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://timothycrosley.github.io/isort/)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![Safety](https://img.shields.io/badge/%20pyupio%20-safety-blue)](https://github.com/pyupio/safety))
- Run containers
- Benchmark with [ab](https://en.wikipedia.org/wiki/ApacheBench)
- Run tests (pass >= [![Coverage](https://img.shields.io/badge/coverage-90%25%2B-brightgreen)](https://github.com/adamwojt/ur_l/actions))
- Push Docker Image

## Credits

- I tried to reference snippets in code
- Build is based on https://github.com/michael0liver/python-poetry-docker-example which was also first presented in here https://github.com/python-poetry/poetry/issues/1879
