#!/bin/sh

ip addr add 192.168.3.13/24 dev net1
ip link set net1 up

ip addr add 192.168.4.17/24 dev net2
ip link set net2 up

pipenv run python3 manage.py migrate --run-syncdb
pipenv run python3 manage.py register_events
pipenv run gunicorn -b 0.0.0.0:8000 server.wsgi 