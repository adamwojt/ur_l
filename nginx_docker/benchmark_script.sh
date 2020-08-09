#!/bin/sh

set -e

ab -k -n 500 -c 10 localhost:80/
#TODO - once API is done

# Can be run with below after docker-compose up:
# docker exec `docker ps -qf "name=ur_l_nginx"` benchmark
