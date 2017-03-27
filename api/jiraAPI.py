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
import api.constants as constants
from jira import JIRA


class JiraAPI(object):

    def __init__(self, user, passwd, logger):
        self.logger = logger
        self.jira = JIRA(server=constants.JIRA_HOST, basic_auth=(user, passwd))

    def get_projects(self):
        self.logger.info("Getting Jira projects")
        json = {'projects': []}
        projects = self.jira.projects()
        for project in projects:
            json.get('projects').append({'id': project.id, 'name': project.name, 'slug': project.key})
        return json

    def get_boards(self):
        self.logger.info("Getting Jira boards")
        json = {'boards': []}
        boards = self.jira.boards()
        for board in boards:
            json.get('boards').append({'id': board.id, 'name': board.name})
        return json

    ### Sprints ###

    def get_project_sprints(self, board_id):
        self.logger.info("Getting board {} sprints".format(board_id))
        json = {'sprints': []}
        sprints = self.jira.sprints(board_id, extended=True)
        for sprint in sprints:
            self.logger.debug("Sprint content: {}".format(sprint.__dict__))
            json.get('sprints').append({'id': sprint.id, 'key': sprint.id, 'name': sprint.name,
                                        'start': sprint.startDate,
                                        'end': sprint.endDate})
        return json

    def search_sprint(self, board_key, sprint_name):
        self.logger.info("Searching board {} sprint '{}'".format(board_key, sprint_name))
        found_sprint = None
        sprints = self.get_project_sprints(board_key)
        for sprint in sprints.get('sprints'):
            if (sprint.get('name') == sprint_name):
                found_sprint = sprint
                break
        return found_sprint

    def create_sprint(self, board_id, sprint_name, start, end):
        self.logger.info("Creating sprint {}".format(sprint_name))
        sprint = self.jira.create_sprint(name=sprint_name, board_id=board_id, startDate=start, endDate=end)
        self.logger.debug("Created sprint {}".format(sprint.__dict__))
        return sprint.id

    def close_sprint(self, sprint_id, start, end):
        self.logger.info("Closing sprint {} [Not working]".format(sprint_id))
        # self.jira.update_sprint(sprint_id, startDate=start, endDate=end, state="Closed")

    def delete_project_sprints(self, board_id):
        self.logger.info("Deleting board {} sprints".format(board_id))
        sprints = self.jira.sprints(board_id, extended=True)
        for sprint in sprints:
            self.logger.info("Deleting sprint {}".format(sprint.name))
            sprint.delete()

    def get_board_project_id(self, board_id):
        self.logger.info("Getting project id of board {}".format(board_id))
        project_id = None
        boards = self.jira.boards()
        for board in boards:
            self.logger.debug("Comparing boards {}-{}".format(board.id, board_id))
            if str(board.id) == str(board_id):
                self.logger.debug("Found matching board {}".format(board.raw))
                project_id = board.raw.get("filter").get("queryProjects").get("projects")[0].get("id")
                break
        return project_id

    ### User stories ###

    def get_project_user_stories(self, project_key):
        self.logger.info("Getting project {} user stories".format(project_key))
        issues = self.jira.search_issues('project=' + project_key + ' and issuetype=Story', json_result=True)
        return issues.get("issues")

    def search_sprint_story(self, project_key, subject):
        self.logger.info("Getting project {} user story with subject: ".format(project_key, subject))
        issues = self.jira.search_issues('project=' + project_key + ' and issuetype=Story and subject='+subject,
                                         json_result=True)
        return issues.get("issues")

    def create_user_story(self, project_id, subject, description, tags, points):
        story_fields = {"project": project_id,
                        "issuetype": "Story",
                        "summary": subject,
                        "description": description,
                        "labels": tags,
                        constants.JIRA_ESTIMATION_FIELD: points}
        created_story = self.jira.create_issue(fields=story_fields)
        self.logger.info("Created user story {} # {}".format(created_story.id, created_story.key))
        self.logger.debug("Created user story details: {}".format(created_story.__dict__))
        return created_story

    def update_user_story_status(self, user_story_key, is_closed, status):
        self.logger.info("Updating user story {} with Taiga status={} ({})".format(user_story_key, status, is_closed))
        if is_closed:
            task_status = constants.JIRA_TASK_STATUS_DONE
            if status == constants.TAIGA_TASK_STATUS_NOT_DONE:
                task_status = constants.JIRA_TASK_STATUS_NOT_DONE
            self.jira.transition_issue(user_story_key, task_status)
            self.logger.info("Updated user story {} status to {}".format(user_story_key, task_status))
        else:
            self.logger.warn("Not updated user story {} beacuse is_closed={}".format(user_story_key, is_closed))

    ### User story tasks ###

    def get_user_story_tasks(self, project_key):
        self.logger.info("Getting project {} user stories".format(project_key))
        issues = self.jira.search_issues('project=' + project_key + ' and issuetype=Sub-task', json_result=True)
        return issues.get("issues")

    def create_user_story_task(self, project_id, user_story_id, subject, description):
        self.logger.info("Creating user story task {}".format(subject))
        created_task = self.jira.create_issue(project=project_id,
                                              parent={"id": user_story_id},
                                              issuetype="Sub-task",
                                              summary=subject)
        self.logger.info("Created user story task {} # {}".format(created_task.id, created_task.key))
        self.logger.debug("Created story task details: {}".format(created_task.__dict__))
        return created_task

    def update_task_status(self, task_key, status):
        self.logger.info("Updating user story task {} with Taiga status={}".format(task_key, status))
        task_status = constants.JIRA_USER_STORY_STATUS_DONE
        if status != constants.TAIGA_USER_STORY_STATUS_NOT_DONE:
            task_status = constants.JIRA_USER_STORY_STATUS_NOT_DONE
        self.jira.transition_issue(task_key, task_status)
        self.logger.info("Updated user story task {} status to {}".format(task_key, task_status))

    ### Sprint creation ###

    def create_sprint_stories(self, board_id, sprint_id, user_stories):
        project_id = self.get_board_project_id(board_id)
        self.logger.info("Creating user stories in project {} - sprint {}".format(project_id, sprint_id))
        user_story = user_stories[0]
        # for user_story in user_stories:
        self.logger.info("Creating user story {}".format(user_story.get("subject")))
        created_story = self.create_user_story(project_id, user_story.get("subject"),
                                               user_story.get("description"),
                                               user_story.get("tags"),
                                               user_story.get("total_points"))
        self.logger.info("Adding user story {} to sprint {}".format(created_story.key, sprint_id))
        self.jira.add_issues_to_sprint(sprint_id, [created_story.key])
        for task in user_story.get("tasks"):
            created_task = self.create_user_story_task(project_id, created_story.id, task.get("subject"),
                                                       task.get("description"))
            self.update_task_status(created_task.key, task.get("status"))
        # self.update_user_story_status(created_story.key, user_story.get("is_closed"), user_story.get("status"))
