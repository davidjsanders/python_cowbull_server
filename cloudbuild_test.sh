#!/usr/bin/env bash
echo "Prepare Redis"
apt-get update && apt-get install -y redis-server
redis-server &
redis_pid=$(ps | grep redis | awk '{print $1;}')
echo "Redis process: "$redis_pid

echo "Re-execute unit tests"
pip install -r requirements.txt
export PYTHONPATH="$(pwd)"
coverage run unittests/main.py
ret_stat="$?"
if [ "$?" != "0" ]; then exit $ret_stat; fi

coverage xml -i
ret_stat="$?"
if [ "$?" != "0" ]; then exit $ret_stat; fi

echo "Execute syystem testts"
export PERSISTER='{"engine_name": "redis", "parameters": {"host": "localhost", "port": 6379, "db": 0, "password": ""}}'
export LOGGING_LEVEL=30
python systests/main.py
ret_stat="$?"
if [ "$?" != "0" ]; then exit $ret_stat; fi
touch coverage.xml

echo "Stop redis ($redis_pid)"
kill $redis_pid

exit $?