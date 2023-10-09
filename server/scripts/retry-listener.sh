#!/bin/sh

ip addr add 192.168.3.15/24 dev net1
ip link set net1 up

ip addr add 192.168.4.19/24 dev net2
ip link set net2 up

pipenv run python3 -u manage.py retry_listener