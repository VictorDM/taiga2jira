#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Copies Taiga sprints, user stories, tasks and backlog information to Jira

Project: Taiga2Jira
Module: Migrator
Class: -
Description: Copies Taiga sprints, user stories, tasks and backlog information to Jira
Authors: Víctor Díaz
License:
"""
from api.jiraAPI import JiraAPI
from api.taigaAPI import TaigaAPI
from api.utils import date_time_to_date_string
from api.utils import date_time_to_jira
import config as config


def auth_taiga(username, password, logger):
    """Init Taiga API authenticating the user with password."""
    taiga_api = TaigaAPI(logger)
    taiga_api.taiga_auth(username, password)
    return taiga_api


def select_taiga_project(taiga_api):
    """Show Taiga  projects and return the key of the project selected by the user."""
    print("### Taiga Projects ###")
    projects = taiga_api.get_projects().get('projects')
    print("KEY # Name")
    for project in projects:
        print("{} # {}".format(project.get('key'), project.get('name')))
    # Get project key
    is_project_key = False
    while not is_project_key:
        project_key = input('Enter Taiga project key: ')
        if not any(proj['key'] == project_key for proj in projects):
            print("Not valid project key: {}".format(project_key))
            is_project_key = False
        else:
            is_project_key = True
    return project_key


def auth_jira(username, password, logger):
    """Init Jira api and authenticates the user woith password."""
    jira_api = JiraAPI(username, password, logger)
    return jira_api


def select_jira_board(jira_api):
    """Show Jira user boards and return the key of the one selected by the user."""
    print("### Jira Boards ###")
    boards = jira_api.get_boards().get('boards')
    print("KEY # Name")
    for board in boards:
        print("{} # {}".format(board.get('id'), board.get('name')))
    # Get board key
    is_board_key = False
    while not is_board_key:
        board_key = input('Enter Jira board key: ')
        if not any(b['id'] == int(board_key) for b in boards):
            print("Not valid board key: {}".format(board_key))
            is_board_key = False
        else:
            is_board_key = True
    sure = input('Are you sure you want to migrate data to board {}? (yes): '.format(board_key))
    if sure != 'yes':
        board_key = None
    return board_key


def _jira_sprint_exists(jira_api, jira_board_key, sprint_name):
    """Check if a sprint already exists in Jira by the sprint name."""
    sprint_id = None
    sprint = jira_api.search_sprint(jira_board_key, sprint_name)
    if sprint:
        sprint_id = sprint.get('id')
    return sprint_id


def _create_jira_sprint_name(sprint_name, sprint_start, sprint_end):
    """Build the sprint name.

    The sprint name depends ont he JIRA_SPRINT_NAME tempalte defined in config.py.
    """
    return config.JIRA_SPRINT_NAME.format(init=date_time_to_date_string(sprint_start),
                                          end=date_time_to_date_string(sprint_end),
                                          name=sprint_name[:config.JIRA_SPRINT_NAME_LENGTH])

def sprints_to_jira(taiga_api, jira_api, taiga_project_key, jira_board_key, logger):
    """Copies all Taiga sprints to jira with their suer stories and tasks.

    First, all sprints are gotten from Taiga and then they are created in Jira.
    If the sprint already exists it won't be created.
    If a user story exists in a srpint it will be duplciated.
    Sprints won't be opened and clsoed because this Jira API funcionnallity does not work.
    User stories status won' be update because if so, stories will be in the sprint but invisible.
    """
    # Get all Taiga sprints
    sprints = taiga_api.get_project_sprints(taiga_project_key)
    # Create each sprint and their stories and tasks in Jira
    for sprint in sprints.get('sprints'):
        sprint_name = _create_jira_sprint_name(sprint.get('name'), sprint.get('start'), sprint.get('end'))
        # Check if sprint exists in Jira
        jira_sprint_id = _jira_sprint_exists(jira_api, jira_board_key, sprint_name)
        # Get taiga sprint begin and end
        sprint_start = date_time_to_jira(sprint.get('start'))
        sprint_end = date_time_to_jira(sprint.get('end'))
        if not jira_sprint_id:
            jira_sprint_id = jira_api.create_sprint(jira_board_key, sprint_name, sprint_start, sprint_end)
            logger.info("Sprint created: {} # {}".format(jira_sprint_id, sprint_name))
        else:
            logger.warn("Sprint not created. Already exists: {}".format(sprint_name))
        # Get Taiga user stories of the sprint with their tasks
        taiga_user_stories = taiga_api.get_sprint_stories(taiga_project_key, sprint.get("id")).get("user_stories")
        # Add user stories with their tasks to the sprint
        created_stories = jira_api.create_sprint_stories(jira_board_key, jira_sprint_id, taiga_user_stories)
        # Start sprint
        # jira_api.start_sprint(jira_sprint_id, sprint_name, sprint_start, sprint_end)
        # Close stories
        # for story in created_stories:
        #     jira_api.update_user_story_status(story.get("key"), story.get("is_closed"), story.get("story.status"))
        # Close sprint
        # jira_api.close_sprint(jira_sprint_id, sprint_name, sprint_start, sprint_end)

def backlog_to_jira(taiga_api, jira_api, taiga_project_key, jira_board_key):
    """Get Taiga backlog stories and copy them into Jira.

    Get all Taiga stories that are not in a sprint and copy to Jira out of any spronts.
    User story order won't be the same in Jira, byut original order and status will be posted as comments.
    """
    backlog = taiga_api.get_backlog_stories(taiga_project_key)
    jira_api.add_backlogs_stories(jira_board_key, backlog.get("user_stories"))
