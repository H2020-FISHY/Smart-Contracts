#!/bin/sh

ip addr add 192.168.3.16/24 dev net1
ip link set net1 up

ip addr add 192.168.4.20/24 dev net2
ip link set net2 up

pipenv run celery -A server.celery worker -l info --without-gossip --without-mingle --without-heartbeat -Ofair -E