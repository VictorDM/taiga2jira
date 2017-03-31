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
import migrator as migrator
from logger import create_app_logger
import getpass


def main():
    logger = create_app_logger()
    logger.info("Starting migration from Taiga to Jira")
    taiga_username = input('Taiga Username: ')
    taiga_password = getpass.getpass(prompt='Taiga Password: ', stream=None)
    # Taiga
    taiga_api = migrator.auth_taiga(taiga_username, taiga_password, logger)
    taiga_project_key = migrator.select_taiga_project(taiga_api)
    # Jira
    jira_username = input('Jira Username: ')
    jira_password = getpass.getpass(prompt='Jira Password: ', stream=None)
    jira_api = migrator.auth_jira(jira_username, jira_password, logger)
    jira_board = migrator.select_jira_board(jira_api)
    if not jira_board:
        logger.info("Cancel migration because Jira board was not confirmed.")
        return
    logger.info("Migrating sprints to Jira")
    migrator.sprints_to_jira(taiga_api, jira_api, taiga_project_key, jira_board, logger)
    logger.info("Migrating backlog to Jira")
    migrator.backlog_to_jira(taiga_api, jira_api, taiga_project_key, jira_board)
    logger.info("End of migration. Good luck!")

if __name__ == '__main__':
    main()
