#!/bin/sh
gunicorn -b 0.0.0.0:$PORT -w 4 main:app
