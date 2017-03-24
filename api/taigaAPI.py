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
from api.utils import taiga_to_date_time
from taiga import TaigaAPI as _TaigaAPI


class TaigaAPI(object):

    def __init__(self, logger):
        self.logger = logger
        self.api = _TaigaAPI(host='https://taiga.i4slabs.com/')

    def taiga_auth(self, user, passwd):
        self.logger.debug("Connecting to Taiga")
        self.api.auth(username=user, password=passwd)
        self.logger.debug("Connecting to Taiga OK")

    def get_projects(self):
        json_projects = {'projects': []}
        projects = self.api.projects.list()
        for project in projects:
            json_projects.get('projects').append({'key': project.slug, 'name': project.name})
        self.logger.debug("Taiga projects: {}".format(json_projects))
        return json_projects

    def get_project_sprints(self, project_id):
        json = {'sprints': []}
        sprints = self.api.projects.get_by_slug(project_id).list_milestones()
        for sprint in sprints:
            json.get('sprints').append({'id': sprint.id, 'key': sprint.slug, 'name': sprint.name,
                                        'start': taiga_to_date_time(sprint.estimated_start),
                                        'end': taiga_to_date_time(sprint.estimated_finish)})
        self.logger.debug("Taiga project {} sprints: {}".format(project_id, json))
        return json

    def get_sprint_stories(self, project_id, sprint_id):
        json = {'user_stories': []}
        sprints = self.api.projects.get_by_slug(project_id).list_milestones()
        for sprint in sprints:
            if sprint.id == sprint_id:
                for user_story in sprint.user_stories:
                    user_story = self.api.projects.get_by_slug(project_id).get_userstory_by_ref(user_story.ref)
                    json_tags = []
                    for tag in user_story.tags:
                        json_tags.append(tag[0])
                    json_tasks = self.get_sprint_story_tasks(project_id, user_story.ref).get('tasks')
                    json.get('user_stories').append({'subject': user_story.subject,
                                                     'description': user_story.description,
                                                     'is_closed': user_story.is_closed,
                                                     'status': user_story.status_extra_info.get("name"),
                                                     'sprint_order': user_story.sprint_order,
                                                     'finish_date': taiga_to_date_time(user_story.finish_date),
                                                     'total_points': user_story.total_points,
                                                     'comment': user_story.comment,
                                                     'tags': json_tags,
                                                     'tasks': json_tasks})
        return json

    def get_sprint_story_tasks(self, project_id, user_story_ref):
        json = {'tasks': []}
        user_story = self.api.projects.get_by_slug(project_id).get_userstory_by_ref(user_story_ref)
        tasks = user_story.list_tasks()
        for task in tasks:
            json.get('tasks').append({'subject': task.subject,
                                      'finished_date': taiga_to_date_time(task.finished_date),
                                      'is_closed': task.is_closed,
                                      'status': task.status_extra_info.get("name")})
        return json
