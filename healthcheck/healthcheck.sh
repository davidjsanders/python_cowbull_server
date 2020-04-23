#!/bin/bash
#set -o pipefail
out=$(curl -sfI http://localhost:8080/v1/modes)
ret_stat=$?
if [ "$ret_stat" == "0" ]
then
    printf "Ready"
    exit 0
else
    printf "Not Ready"
    exit 1
fi
