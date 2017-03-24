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
from jira import JIRA


class JiraAPI(object):

    def __init__(self, user, passwd, logger):
        self.logger = logger
        self.jira = JIRA(server='https://innovation4security.atlassian.net', basic_auth=(user, passwd))

    def get_projects(self):
        json = {'projects': []}
        projects = self.jira.projects()
        for project in projects:
            json.get('projects').append({'id': project.id, 'name': project.name, 'slug': project.key})
        return json

    def get_boards(self):
        json = {'boards': []}
        boards = self.jira.boards()
        for board in boards:
            json.get('boards').append({'id': board.id, 'name': board.name})
        return json

    def get_project_sprints(self, board_id):
        json = {'sprints': []}
        sprints = self.jira.sprints(board_id, extended=True)
        for sprint in sprints:
            self.logger.debug("Sprint content: {}".format(sprint.__dict__))
            json.get('sprints').append({'id': sprint.id, 'key': sprint.id, 'name': sprint.name,
                                        'start': sprint.startDate,
                                        'end': sprint.endDate})
        return json

    def search_sprint(self, board_key, sprint_name):
        found_sprint = None
        sprints = self.get_project_sprints(board_key)
        for sprint in sprints.get('sprints'):
            if (sprint.get('name') == sprint_name):
                found_sprint = sprint
                break
        return found_sprint

    def create_sprint(self, board_id, sprint_name, start, end):
        sprint = self.jira.create_sprint(name=sprint_name, board_id=board_id, startDate=start, endDate=end)
        return sprint.id

    def close_sprint(self, sprint_id, start, end):
        self.logger.info("Closing sprint {} [Not working]".format(sprint_id))
        # self.jira.transition_issue(sprint_id, "Closed")
        self.jira.update_sprint(sprint_id, startDate=start, endDate=end, state="Closed")

    def delete_project_sprints(self, board_id):
        sprints = self.jira.sprints(board_id, extended=True)
        for sprint in sprints:
            self.logger.info("Deleting sprint {}".format(sprint.name))
            sprint.delete()

    def get_board_project_id(self, board_id):
        project_id = None
        boards = self.jira.boards()
        self.logger.debug("Searching project for board {}".format(board_id))
        for board in boards:
            self.logger.debug("Comparing boards {}-{}".format(board.id, board_id))
            if str(board.id) == str(board_id):
                self.logger.debug("Found matching board {}".format(board.raw))
                project_id = board.raw.get("filter").get("queryProjects").get("projects")[0].get("id")
                break
        return project_id

    def get_sprint_stories(self):
        issues = self.jira.search_issues('project=LUXIDMTEST and issuetype=Story', json_result=True)
        self.logger.info("\n*** User stories:")
        for issue in issues.get("issues"):
            self.logger.info("\nUser story: {}".format(issue))

    def search_sprint_story(self, subject):
        issues = self.jira.search_issues('project=LUXIDMTEST and issuetype=Story and subject='+subject, json_result=True)
        self.logger.info("\n*** User stories:")
        for issue in issues.get("issues"):
            self.logger.info("\nUser story: {}".format(issue))

    def create_user_story(self, project_id, subject, description, tags, points):
        created_story = self.jira.create_issue(project=project_id,
                                               issuetype="Story",
                                               summary=subject,
                                               description=description,
                                               labels=tags)
        self.logger.info("Created sprint story {}".format(created_story.key))
        self.logger.debug("Created sprint story details: {}".format(created_story.__dict__))
        self.jira.add_worklog(created_story.id, timeSpent="20d", adjustEstimate="auto", newEstimate="20d")
        return created_story

    def get_user_story_tasks(self):
        issues = self.jira.search_issues('project=LUXIDMTEST and issuetype=Sub-task', json_result=True)
        self.logger.info("\n*** User story tasks:")
        for issue in issues.get("issues"):
            self.logger.info("\nUser story task: {}".format(issue))

    def create_story_task(self, project_id, user_story_id, subject, description):
        created_task = self.jira.create_issue(project=project_id,
                                              parent={"id": user_story_id},
                                              issuetype="Sub-task",
                                              summary=subject)
        self.logger.info("Created story task {}".format(created_task.key))
        self.logger.debug("Created story task details: {}".format(created_task.__dict__))
        self.jira.transition_issue(created_task.key, "Done")
        return created_task

    def create_sprint_stories(self, board_id, sprint_id, user_stories):
        project_id = self.get_board_project_id(board_id)
        self.logger.info("Creating user stories in project {} - sprint {}".format(project_id, sprint_id))
        issues_key = []
        for user_story in user_stories:
            # print(user_story)
            created_story = self.create_user_story(project_id, user_story.get("subject"),
                                                   user_story.get("description"),
                                                   user_story.get("tags"),
                                                   user_story.get("total_points"))

            issues_key.append(created_story.key)
            for task in user_story.get("tasks"):
                self.create_story_task(project_id, created_story.id, task.get("subject"), task.get("description"))
            #self.jira.transition_issue(created_story.key, "Done")
        self.jira.add_issues_to_sprint(sprint_id, issues_key)
        # self.get_sprint_stories()
