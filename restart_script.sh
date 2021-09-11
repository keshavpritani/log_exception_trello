#!/bin/bash

screen -S log_exception -X quit
screen -dmS log_exception bash -c '/usr/bin/python3 /home/centos/log_exception_trello/read_log.py'