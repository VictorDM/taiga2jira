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
import logging


def create_app_logger():
    """Create application logger using Sysloghandler.

    :returns: Logger used to write application logs
    :rtype: logging.Logger
    """
    logger = logging.getLogger('taiga2jira')
    logger_formatter = logging.Formatter('%(levelname)s %(message)s')
    # Log Handler
    handler = logging.StreamHandler()
    handler.setFormatter(logger_formatter)
    logger.addHandler(handler)
    # Set logger level
    logger.setLevel(logging.INFO)
    return logger
