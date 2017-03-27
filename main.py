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
from api.taigaAPI import TaigaAPI
from api.jiraAPI import JiraAPI
from api.utils import date_time_to_jira
from logger import create_app_logger
import getpass


def auth_taiga(username, password, logger):
    taiga_api = TaigaAPI(logger)
    taiga_api.taiga_auth(username, password)
    return taiga_api

def select_taiga_project(taiga_api):
    print("### Taiga Projects ###")
    projects = taiga_api.get_projects()
    print("KEY # Name")
    for project in (projects.get('projects')):
        print("{} # {}".format(project.get('key'), project.get('name')))
    # Get project key
    # project_key = input('Enter Taiga project key: ')
    project_key = 'i4s-lux-idm'
    return project_key

def show_taiga_sprints(taiga_api, taiga_project_key):
    sprints = taiga_api.get_project_sprints(taiga_project_key)
    print("### Project Sprints ###")
    print("KEY # Name [Start][End]")
    for sprint in sprints.get('sprints'):
        print("{} # '{}' [{}]-[{}]".format(sprint.get('key'), sprint.get('name'), sprint.get('start'),
                                           sprint.get('end')))

def auth_jira(username, password, logger):
    jira_api = JiraAPI(username, password, logger)
    return jira_api

def select_jira_board(jira_api):
    print("### Jira Boards ###")
    boards = jira_api.get_boards()
    print("KEY # Name")
    for board in (boards.get('boards')):
        print("{} # {}".format(board.get('id'), board.get('name')))
    # board_key = input('Enter Jira board key: ')
    board_key = "20"
    return board_key

def show_jira_sprints(jira_api, jira_board_key):
    print("### Project Sprints ###")
    sprints = jira_api.get_project_sprints(jira_board_key)
    print("KEY # Name [Start][End]")
    for sprint in sprints.get('sprints'):
        print("{} # '{}' [{}]-[{}]".format(sprint.get('key'), sprint.get('name'), sprint.get('start'),
                                           sprint.get('end')))

def jira_sprint_exists(jira_api, jira_board_key, sprint_name):
    sprint_id = None
    sprint = jira_api.search_sprint(jira_board_key, sprint_name)
    if sprint:
        sprint_id = sprint.get('id')
    return sprint_id

def sprints_to_jira(taiga_api, jira_api, taiga_project_key, jira_board_key, logger):
    # Get all Taiga sprints
    sprints = taiga_api.get_project_sprints(taiga_project_key)
    # Create each sprint and their stories and tasks in Jira
    for sprint in sprints.get('sprints'):
        sprint_name = sprint.get('name')[:30]
        if sprint_name == 'S52 - Agoreeeeeeer':
            # Check if sprint exists in Jira
            jira_sprint_id = jira_sprint_exists(jira_api, jira_board_key, sprint_name)
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
            jira_api.create_sprint_stories(jira_board_key, jira_sprint_id, taiga_user_stories)
            # Close sprint
            jira_api.close_sprint(jira_sprint_id, sprint_start, sprint_end)

def main():
    logger = create_app_logger()
    logger.info("Starting migration from Taiga to Jira")
    taiga_username = input('Taiga Username: ')
    taiga_password = getpass.getpass(prompt='Taia Password: ', stream=None)
    # Taiga
    taiga_api = auth_taiga(taiga_username, taiga_password, logger)
    taiga_project = select_taiga_project(taiga_api)
    # show_taiga_sprints(taiga_api, taiga_project)
    # Jira
    jira_username = input('Jira Username: ')
    jira_password = getpass.getpass(prompt='Jira Password: ', stream=None)
    jira_api = auth_jira(jira_username, jira_password, logger)
    jira_board = select_jira_board(jira_api)
    # jira_api.get_project_sprints(jira_board)
    # jira_api.delete_project_sprints(jira_board)
    sprints_to_jira(taiga_api, jira_api, taiga_project, jira_board, logger)
    # show_jira_sprints(jira_api, jira_board)
    logger.info("End of migration. Good luck!")

if __name__ == '__main__':
    main()
