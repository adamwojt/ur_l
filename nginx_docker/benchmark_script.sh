#!/bin/sh

set -e

API_ROOT=localhost:80/
API_URL=${API_ROOT}api/urls/
DATA='{"long_url":"www.google.com"}'

# Let's post to get token first
TOKEN=`curl --header "Content-Type: application/json" \
--request POST --data $DATA \
${API_ROOT}api/urls/ | jq -r '.token'`

# Now let's make 5000 requests to fetch this token.
ab -k -n 5000 -c 10 ${API_ROOT}$TOKEN

echo $DATA > /tmp/data.json

# Now let's make 5000 requests to create
ab -p /tmp/data.json -T application/json -c 10 -n 5000 $API_URL
