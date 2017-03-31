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

TAIGA_HOST = ''
JIRA_HOST = ''
# User story points custom field of Jira
JIRA_ESTIMATION_FIELD = "customfield_10004"
# Taiga status that means a task is done
TAIGA_TASK_STATUS_DONE = "Done"
# Jira status that means a task is done
JIRA_TASK_STATUS_DONE = "Done"
# Jira status that means a task is not done
JIRA_TASK_STATUS_NOT_DONE = "Not Done"
# Taiga status that means a user story is done
TAIGA_USER_STORY_STATUS_NOT_DONE = "Not Done"
# Jira status that means a user story is done
JIRA_USER_STORY_STATUS_DONE = "Done"
# Jira status that means a user story is not done
JIRA_USER_STORY_STATUS_NOT_DONE = "Not Done"
# Task type of a User story sub-task issue
JIRA_USER_STORY_TASK_TYPE = "Sub-task"
# Task type of a User story issue
JIRA_USER_STORY_TYPE = "Story"
# init = init date, end = end date, name = sprit_name[:JIRA_SPRINT_NAME_LENGTH]
JIRA_SPRINT_NAME = "{init}-{end} {name}"
# Sprint name length is the part of the Taiga sprint name that will be stored in Jira.
# Jira sprint names are up to 30 chars, so if dates are added to sprint name length must be shortened.
JIRA_SPRINT_NAME_LENGTH = 12
