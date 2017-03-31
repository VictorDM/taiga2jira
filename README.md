# taiga2jira
Taiga migration to Jira tool

This script migrates all of the sprints of a Taiga project, with their user stories and tasks and the backlog user stories to Jira.

# Migration steps

1. Install python3
2. Install project requirements
```
$ pip install -r requirements.txt
```
3. Configure the values of the config.py file
 * TAIGA_HOST: URL of Taiga
 * JIRA_HOST = URL of Jira
 * JIRA_ESTIMATION_FIELD: User story points custom field of Jira
 * TAIGA_TASK_STATUS_DONE: Taiga status that means a task is done
 * JIRA_TASK_STATUS_DONE: Jira status that means a task is done
 * JIRA_TASK_STATUS_NOT_DONE: Jira status that means a task is not done
 * TAIGA_USER_STORY_STATUS_NOT_DONE: Taiga status that means a user story is done
 * JIRA_USER_STORY_STATUS_DONE: Jira status that means a user story is done
 * JIRA_USER_STORY_STATUS_NOT_DONE: Jira status that means a user story is not done
 * JIRA_USER_STORY_TASK_TYPE: Task type of a User story sub-task issue
 * JIRA_USER_STORY_TYPE: Task type of a User story issue
 * JIRA_SPRINT_NAME: Jira sprint name template. The template has the following params: init, end, name. Default template is "{init}-{end} {name[:JIRA_SPRINT_NAME_LENGTH]}"
 * JIRA_SPRINT_NAME_LENGTH: print name length is the part of the Taiga sprint name that will be stored in Jira. Jira sprint names are up to 30 chars, so if dates are added to sprint name length must be shortened.

4. Launch the migrator
```
$ python3 main.yml
```


# Info that is migrated

## Sprints

Sprints are created with their name, start date and end date.

| Field | Jira field | Taiga field|
|-------|------|-------|
|Name|name|name|
|Start date|startDate|start|
|End date|endDate|end|

## User stories

User stories are created inside their sprint with the following fields:

| Field | Jira field | Taiga field|
|-------|------|-------|
|Summary|summary|subject|
|Description|description|description|
|Labels|labels|tags|
|Story points|config.JIRA_ESTIMATION_FIELD|points|
*In order to create the story points in Jira, a custom field name Story points must be created (Project settings --> Custom fields) and added to the Story screen (Project settings --> Screens). Then, the id of the field must be set in the config.py file in 'JIRA_ESTIMATION_FIELD' constant.*

User story status i not updated. If the story status is updated it won't be visible inside the sprint unless you create a fake story and start the sprint.
Taiga status and finished date are added as story comments.

## User story tasks

The sub-tasks of a user story are created with the following fields

| Field | Jira field | Taiga field|
|-------|------|-------|
|Summary|summary|subject|

After creating the tasks, they are updated follwing the rule:

If task is not in Taiga in Done status (TAIGA_TASK_STATUS_DONE), in Jira is created as Not Done status (JIRA_TASK_STATUS_NOT_DONE). Otherwise is updated to Done (JIRA_TASK_STATUS_DONE). *(Uppercase words are constants defined in config.py)*
Taiga status and finished date are added as task comments.

# Known issues

* Sprints can't be opened nor closed. Jira api call to update sprint does not have 'state' var in the Java api implementation. Updating a sprint using API rest and state parameter causes Exception.
* User story status is not updated inside a sprint because that will make it unvisible inside the sprint until you create a fake issue and open the sprint.
