#!/bin/sh
gunicorn -b 0.0.0.0:$PORT -w $WORKERS main:app
