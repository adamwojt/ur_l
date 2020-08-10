#!/bin/sh

n=0
until [ "$n" -ge 5 ]
do
   DATA_CURL=$(curl --header "Content-Type: application/json" --request POST --data @./benchmark.json --url localhost:80/api/urls/)
   TOKEN=`echo $DATA_CURL | jq -r '.token'` && break
   n=$((n+1)) 
   sleep 15
done

# Now let's make 5000 requests to fetch this token.
ab -k -n 5000 -c 10 localhost:80/$TOKEN

# Now let's make 5000 requests to create
ab -p benchmark.json -T application/json -c 10 -n 5000 localhost:80/api/urls/
