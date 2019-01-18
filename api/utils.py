#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Conversions between Taiga and Jira formats.

Project: Taiga2Jira
Module: Utils
Class: -
Description: Conversions between Taiga and Jira formats
Authors: Víctor Díaz
License:
"""
import datetime


def taiga_to_date_time(str_date_time):
    """Convert taiga date time string to python datetime."""
    print("Date time string: {}".format(str_date_time))
    if str_date_time is None:
        return None
    else:
        datetime_format = '%Y-%m-%d'
        if len(str_date_time) == 27:
            datetime_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        return datetime.datetime.strptime(str_date_time, datetime_format)


def date_time_to_jira(date_time):
    """Convert python datetime to Jira format with 01:00 as default hour."""
    if date_time is None:
        return None
    else:
        return date_time.strftime('%d/%b/%y 01:00 %p')


def date_time_to_date_string(date_time):
    """Convert python datetime to a YYYYmmdd string format."""
    if date_time is None:
        return None
    else:
        return date_time.strftime('%Y%m%d')
