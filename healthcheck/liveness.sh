#!/bin/bash
#set -o pipefail
output=$(curl -s http://localhost:8080/v1/health)
grepout=$(echo $output | grep "notok")
if [ "$grepout" == "" ]; 
then 
    printf "Healthy"
    exit 0; 
else 
    printf "Unhealthy --> ${output}"
    exit 1; 
fi
