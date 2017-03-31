#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Taiga Api access using python-taiga project

Project: Taiga2Jira
Module: api
Class: TaigaAPI
Description: Access Taiga API and performs read operations over it.
Authors: Víctor Díaz
License:
"""
from api.utils import taiga_to_date_time
import config as config
from taiga import TaigaAPI as _TaigaAPI
from tqdm import tqdm


class TaigaAPI(object):
    """Access Taiga API using python-taiga project."""

    def __init__(self, logger):
        """Init TaigaAPI object and logger."""
        self.logger = logger
        self.api = _TaigaAPI(host=config.TAIGA_HOST)

    def taiga_auth(self, user, passwd):
        """Authenticate user with password in Taiga api."""
        self.logger.info("Connecting to Taiga")
        self.api.auth(username=user, password=passwd)
        self.logger.info("Connecting to Taiga OK")

    def get_projects(self):
        """Build a json with all projects in Taiga."""
        self.logger.debug("Taiga getting projects")
        json_projects = {'projects': []}
        projects = self.api.projects.list()
        for project in projects:
            json_projects.get('projects').append({'key': project.slug, 'name': project.name})
        # self.logger.debug("Taiga projects: {}".format(json_projects))
        return json_projects

    def get_project_sprints(self, project_key):
        """Build a json with all of the sprints of a project.

        Content of the sprints won't be added.
        """
        self.logger.info("Taiga getting project {} sprints".format(project_key))
        json = {'sprints': []}
        sprints = self.api.projects.get_by_slug(project_key).list_milestones()
        for sprint in tqdm(sprints):
            json_sprint = {'id': sprint.id,
                           'key': sprint.slug,
                           'name': sprint.name,
                           'start': taiga_to_date_time(sprint.estimated_start),
                           'end': taiga_to_date_time(sprint.estimated_finish)
                           }
            json.get('sprints').append(json_sprint)
            # self.logger.debug("Taiga Project {} - Sprint: {}\n{}".format(project_key, sprint.id, json_sprint))
        return json

    def _get_user_story_tasks(self, project_key, user_story_ref):
        """Get the tasks of a user story as json."""
        self.logger.debug("Taiga getting project {} user story {} tasks".format(project_key, user_story_ref))
        json = {'tasks': []}
        user_story = self.api.projects.get_by_slug(project_key).get_userstory_by_ref(user_story_ref)
        tasks = user_story.list_tasks()
        for task in tasks:
            json.get('tasks').append({'subject': task.subject,
                                      'finished_date': taiga_to_date_time(task.finished_date),
                                      'is_closed': task.is_closed,
                                      'status': task.status_extra_info.get("name")})
        return json

    def _create_user_story_json(self, user_story, project_key):
        """Build a json with a user story and its tasks."""
        json_tags = []
        for tag in user_story.tags:
            json_tags.append(tag[0].replace(" ", "_"))
        json_tasks = self._get_user_story_tasks(project_key, user_story.ref).get('tasks')
        json_user_story = {'subject': user_story.subject,
                           'description': user_story.description,
                           'is_closed': user_story.is_closed,
                           'status': user_story.status_extra_info.get("name"),
                           'finish_date': taiga_to_date_time(user_story.finish_date),
                           'total_points': user_story.total_points,
                           'tags': json_tags,
                           'backlog_order': user_story.backlog_order,
                           'tasks': json_tasks}
        return json_user_story

    def get_backlog_stories(self, project_key):
        """Build a json with all user stories that are in the backlog  (not in a sprint)."""
        self.logger.info("Taiga getting project {} backlog user stories".format(project_key))
        json = {'user_stories': []}
        user_stories = self.api.projects.get_by_slug(project_key).list_user_stories()
        for user_story in tqdm(user_stories):
            user_story = self.api.projects.get_by_slug(project_key).get_userstory_by_ref(user_story.ref)
            if user_story.milestone is None:
                json.get('user_stories').append(self._create_user_story_json(user_story, project_key))
        return json

    def get_sprint_stories(self, project_key, sprint_id):
        """Build a json with all the stories of a sprint."""
        self.logger.debug("Taiga getting project {} sprint {} user stories".format(project_key, sprint_id))
        json = {'user_stories': []}
        sprints = self.api.projects.get_by_slug(project_key).list_milestones()
        for sprint in sprints:
            if sprint.id == sprint_id:
                for user_story in sprint.user_stories:
                    user_story = self.api.projects.get_by_slug(project_key).get_userstory_by_ref(user_story.ref)
                    json.get('user_stories').append(self._create_user_story_json(user_story, project_key))
        return json
