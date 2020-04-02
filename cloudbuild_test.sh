#!/usr/bin/env sh
pip install -r requirements.txt
export PYTHONPATH="$(pwd)"
coverage run unittests/main.py
coverage xml -i
export PERSISTER='{"engine_name": "redis", "parameters": {"host": "localhost", "port": 6379, "db": 0, "password": ""}}'
export LOGGING_LEVEL=30
docker run -d --rm --name redis -p 6379:6379 redis:alpine3.11
python systests/main.py
docker stop redis
exit $?