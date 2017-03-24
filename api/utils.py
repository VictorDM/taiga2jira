#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Import data from Taiga to Jira.

Project: Taiga2Jira
Module: Main
Class: -
Description: Main file
Authors: Víctor Díaz
License:
"""
import datetime


def taiga_to_date_time(str_date_time):
    datetime_format = '%Y-%m-%d'
    if len(str_date_time) == 27:
        datetime_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    return datetime.datetime.strptime(str_date_time, datetime_format)


def date_time_to_jira(date_time):
    return date_time.strftime('%d/%b/%y 01:00 %p')
