#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Import data from Taiga to Jira.

Project: Taiga2Jira
Module: Logger
Description: Logs operations to stdout and log file
Authors: Víctor Díaz
License:
"""
import logging
from time import gmtime
from time import strftime


def create_app_logger():
    """Create application logger using Sysloghandler.

    :returns: Logger used to write application logs
    :rtype: logging.Logger
    """
    logger = logging.getLogger('taiga2jira')
    logger_formatter = logging.Formatter('%(levelname)s %(message)s')
    # Stdout Log Handler
    handler = logging.StreamHandler()
    handler.setFormatter(logger_formatter)
    logger.addHandler(handler)
    # Log File handler
    file_handler = logging.FileHandler("taiga2jira_{}.log".format(strftime("%Y-%m-%d %H:%M:%S", gmtime())))
    file_handler.setFormatter(logger_formatter)
    logger.addHandler(file_handler)
    # Set logger level
    logger.setLevel(logging.INFO)
    return logger
