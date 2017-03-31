#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Access Jira api using python-jira project.

Project: Taiga2Jira
Module: api
Class: JiraAPI
Description: Access Jira api using python-jira project.
Authors: Víctor Díaz
License:
"""
import config as config
from jira import JIRA
from tqdm import tqdm


class JiraAPI(object):
    """Access Jira api using python-jira project."""

    def __init__(self, user, passwd, logger):
        """Init JiraApi object and logger."""
        self.logger = logger
        self.jira = JIRA(server=config.JIRA_HOST, basic_auth=(user, passwd))

    def get_boards(self):
        """Get Jira boards list as json."""
        self.logger.info("Getting Jira boards")
        json = {'boards': []}
        boards = self.jira.boards()
        for board in boards:
            json.get('boards').append({'id': board.id, 'name': board.name})
        return json

    # ###############
    # ### Sprints ###
    # ###############

    def _get_board_sprints(self, board_id):
        """Get sprints of a board as json."""
        self.logger.info("Getting board {} sprints".format(board_id))
        json = {'sprints': []}
        sprints = self.jira.sprints(board_id, extended=True)
        for sprint in sprints:
            # self.logger.debug("Sprint content: {}".format(sprint.__dict__))
            json.get('sprints').append({'id': sprint.id, 'key': sprint.id, 'name': sprint.name,
                                        'start': sprint.startDate,
                                        'end': sprint.endDate})
        return json

    def search_sprint(self, board_key, sprint_name):
        """Search a sprint in a board and returns its info."""
        self.logger.info("Searching board {} sprint '{}'".format(board_key, sprint_name))
        found_sprint = None
        sprints = self._get_board_sprints(board_key)
        for sprint in sprints.get('sprints'):
            if (sprint.get('name') == sprint_name):
                found_sprint = sprint
                break
        return found_sprint

    def create_sprint(self, board_id, sprint_name, start, end):
        """Create a sprint in a board with given start and end dates.

        Dates must be in Jira format.
        """
        self.logger.info("Creating sprint {}".format(sprint_name))
        sprint = self.jira.create_sprint(name=sprint_name, board_id=board_id, startDate=start, endDate=end)
        # self.logger.debug("Created sprint content {}".format(sprint.__dict__))
        return sprint.id

    def start_sprint(self, sprint_id, sprint_name, start, end):
        """Start a Jira sprint with given dates. *** Does not work because Jira API call fails with 'state' param. ***

        Dates must be in Jira format.
        """
        self.logger.info("Starting sprint {} [Not working]".format(sprint_id))
        # self.jira.update_sprint(sprint_id, name=sprint_name, startDate=start, endDate=end, state="active")

    def close_sprint(self, sprint_id, sprint_name, start, end):
        """Closes a Jira sprint with given dates. *** Does not work because Jira API call fails with 'state' param. ***

        Dates must be in Jira format.
        """
        self.logger.info("Closing sprint {} [Not working]".format(sprint_id))
        # self.jira.update_sprint(sprint_id, name=sprint_name, startDate=start, endDate=end, state=None)

    def delete_board_sprints(self, board_id):
        """Delete all sprints of a board."""
        self.logger.info("Deleting board {} sprints".format(board_id))
        sprints = self.jira.sprints(board_id, extended=False)
        for sprint in tqdm(sprints):
            self.logger.info("Deleting sprint {}".format(sprint.name))
            sprint.delete()

    def _get_board_project_id(self, board_id):
        """Get the project id of a board."""
        self.logger.debug("Getting project id of board {}".format(board_id))
        project_id = None
        boards = self.jira.boards()
        for board in boards:
            # self.logger.debug("Comparing boards {}-{}".format(board.id, board_id))
            if str(board.id) == str(board_id):
                # self.logger.debug("Found matching board {}".format(board.raw))
                project_id = board.raw.get("filter").get("queryProjects").get("projects")[0].get("id")
                break
        return project_id

    # ####################
    # ### User stories ###
    # ####################

    def _get_project_user_stories(self, project_key):
        """Get all user stories of a project."""
        self.logger.info("Getting project {} user stories".format(project_key))
        issues = self.jira.search_issues('project=' + project_key + ' and issuetype=' + config.JIRA_USER_STORY_TYPE,
                                         maxResults=200)
        return issues

    def delete_all_project_user_stories(self, project_key):
        """Delete all user stories of a project."""
        self.logger.info("Deleting project {} user stories".format(project_key))
        issues = self._get_project_user_stories(project_key)
        for issue in tqdm(issues):
            self.logger.info("Deleting user story {}".format(issue))
            issue.delete()

    def _create_user_story(self, project_id, subject, description, tags, points):
        """Create a user story with provided information."""
        story_fields = {"project": project_id,
                        "issuetype": config.JIRA_USER_STORY_TYPE,
                        "summary": subject,
                        "description": description,
                        "labels": tags,
                        config.JIRA_ESTIMATION_FIELD: points}
        created_story = self.jira.create_issue(fields=story_fields)
        self.logger.info("Created user story {} # {}".format(created_story.id, created_story.key))
        # self.logger.debug("Created user story details: {}".format(created_story.__dict__))
        return created_story

    def update_user_story_status(self, user_story_key, is_closed, status):
        """Update the status of a user story to Done or Not Done only if it's closed.

        A translation is made between the status given, which is the status in Taiga and the Jira status as
        defined in JIRA_USER_STORY_STATUS_DONE, JIRA_USER_STORY_STATUS_NOT_DONE and TAIGA_USER_STORY_STATUS_NOT_DONE
        constants of config.py file.
        """
        self.logger.info("Updating user story {} with Taiga status={} ({})".format(user_story_key, status, is_closed))
        if is_closed:
            task_status = config.JIRA_USER_STORY_STATUS_DONE
            if status == config.TAIGA_USER_STORY_STATUS_NOT_DONE:
                task_status = config.JIRA_USER_STORY_STATUS_NOT_DONE
            self.jira.transition_issue(user_story_key, task_status)
            self.logger.info("Updated user story {} status to {}".format(user_story_key, task_status))
        else:
            self.logger.warn("Not updated user story {} beacuse is not closed: is_closed={}".format(user_story_key,
                                                                                                    is_closed))

    # ########################
    # ### User story tasks ###
    # ########################

    def _create_user_story_task(self, project_id, user_story_id, subject, description, finished_date):
        """Create a task inside a user story.

        The story task type is defined in config.py in JIRA_USER_STORY_TASK_TYPE constant. default is 'Sub-type'.
        """
        self.logger.info("Creating user story task {}".format(subject))
        created_task = self.jira.create_issue(project=project_id,
                                              parent={"id": user_story_id},
                                              issuetype=config.JIRA_USER_STORY_TASK_TYPE,
                                              summary=subject)
        self.logger.info("Created user story task {} # {}".format(created_task.id, created_task.key))
        # self.logger.debug("Created story task details: {}".format(created_task.__dict__))
        return created_task

    def _update_task_status(self, task_key, status):
        """Update task status with Done or not Done status depending on incoming Taiga status.

        Taiga done status is defined in TAIGA_TASK_STATUS_DONE constant inside config.py file.
        Jira done and not done statuses are defined in JIRA_TASK_STATUS_DONE and JIRA_TASK_STATUS_NOT_DONE inside
        config.py file.
        """
        self.logger.info("Updating user story task {} with Taiga status={}".format(task_key, status))
        task_status = config.JIRA_TASK_STATUS_DONE
        if status != config.TAIGA_TASK_STATUS_DONE:
            task_status = config.JIRA_TASK_STATUS_NOT_DONE
        self.jira.transition_issue(task_key, task_status)
        self.logger.info("Updated user story task {} status to {}".format(task_key, task_status))

    # #######################
    # ### Sprint creation ###
    # #######################

    def _add_comment(self, issue_id, comment):
        """Add a comment to an issue."""
        self.logger.debug("Adding comment to issue {}".format(issue_id))
        self.jira.add_comment(issue_id, comment, visibility={'group': 'jira-users'})

    def create_sprint_stories(self, board_id, sprint_id, user_stories):
        """Create user stories in a board and link them to a sprint.

        A json array with user story key, is_closed and status info is returned.
        User stories subtasks are also added to the story.
        User story tasks finished date and current taiga status are added as comments.
        User story finished date and current taiga status are added as comments.
        """
        project_id = self._get_board_project_id(board_id)
        self.logger.info("Creating user stories in project {} - sprint {}".format(project_id, sprint_id))
        created_stories = []
        for user_story in user_stories:
            self.logger.info("Creating user story {}".format(user_story.get("subject")))
            created_story = self._create_user_story(project_id, user_story.get("subject"),
                                                    user_story.get("description"),
                                                    user_story.get("tags"),
                                                    user_story.get("total_points"))
            self.logger.info("Adding user story {} to sprint {}".format(created_story.key, sprint_id))
            self.jira.add_issues_to_sprint(sprint_id, [created_story.key])
            for task in user_story.get("tasks"):
                created_task = self._create_user_story_task(project_id, created_story.id, task.get("subject"),
                                                            task.get("description"), task.get("finished_date"))
                # Add as comment user story finished date
                self._add_comment(created_task.id, "Finished date: '{}'".format(task.get('finished_date')))
                self._add_comment(created_task.id, "Taiga status: '{}'".format(task.get("status")))
                # Update task status
                self._update_task_status(created_task.key, task.get("status"))
            created_stories.append({"key": created_story.key,
                                    "is_closed": user_story.get("is_closed"),
                                    "status": user_story.get("status")})
            # Add as comment user story finished date
            self._add_comment(created_story.id, "Finished date: '{}'".format(user_story.get('finish_date')))
            self._add_comment(created_story.id, "Taiga status: '{}'".format(user_story.get("status")))
        return created_stories

    def add_backlogs_stories(self, board_id, user_stories):
        """Add user stories to the backlog of the board.

        Taiga original status and backlog order are added as comments.
        """
        project_id = self._get_board_project_id(board_id)
        self.logger.info("Creating user stories in project {} backlog".format(project_id))
        created_stories = []
        for user_story in user_stories:
            self.logger.info("Creating user story {}".format(user_story.get("subject")))
            created_story = self._create_user_story(project_id, user_story.get("subject"),
                                                    user_story.get("description"),
                                                    user_story.get("tags"),
                                                    user_story.get("total_points"))
            created_stories.append({"key": created_story.key})
            # Add as comment user story finished date
            self._add_comment(created_story.id, "Taiga status: '{}'".format(user_story.get("status")))
            self._add_comment(created_story.id, "Taiga backlog order: '{}'".format(user_story.get("backlog_order")))
        return created_stories
