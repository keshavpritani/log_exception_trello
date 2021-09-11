#!/bin/bash

process_id=`ps f | grep read_log | awk 'NR==1 {print $1}'`

if [ process_id != "" ]; then
	kill -9 process_id
	nohup python3 /home/centos/log_exception_trello/read_log.py &
fi