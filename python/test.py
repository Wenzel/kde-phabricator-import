#!/usr/bin/env python

# sys
import os
import sys
import re
import logging

# local
# from tools.wmfphablib import phabdb
import config
import kanDB
from pprint import pprint

# 3rd
from phabricator import Phabricator

# conduit API
conduit = Phabricator(host=config.CONDUIT_HOST,
                   token=config.CONDUIT_TOKEN)
conduit.update_interfaces()

def init_logger():
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

# check if a given project is present in phabricator
# if not, it will be created
def checkProject(project):
    logging.debug('Checking for project [{}]'.format(project.name))
    rep = conduit.project.query(names=[project.name])
    if not rep['data']:
        logging.debug('Creating project [{}]'.format(projectname))
        rep = conduit.project.create(name=project.name, members=[])
        # TODO check rep
    # getting phid
    rep = conduit.project.query(names=[project.name])
    (project_phid, info) = rep['data'].items()[0]
    return project_phid

def checkTask(project_phid, task):
    logging.debug('\tChecking for task [{}]'.format(task.title))
    rep = conduit.maniphest.query(projectPHIDs=[project_phid])
    task_phid = None
    for key, value in rep.items():
        if value['title'] == task.title:
            task_phid = key
            # task_subtasks_phids = value['dependsOnTaskPHIDs']
            break
    if task_phid is None:
        # must create task
        logging.debug('\tCreating task [{}]'.format(task.title))
        rep = conduit.maniphest.createtask(title=task.title,
                description=task.description,
                projectPHIDs=[project_phid])
        # TODO check rep
        task_phid = rep['phid']
    return task_phid

def checkSubtask(project_phid, task_phid, subtask):
    logging.debug('\t\tChecking for subtask [{}]'.format(subtask.title))
    # query all subtasks of task_phid
    rep = conduit.maniphest.query(projectPHIDs=[project_phid], phids=[task_phid])
    (id, info) = rep.items()[0]
    task_subtask_phid_list = info['dependsOnTaskPHIDs']
    # iterate on each of these subtask
    # to see if we already exist
    subtask_phid = None
    for existing_subtack_phid in task_subtask_phid_list:
        rep = conduit.maniphest.query(phids=[existing_subtask_phid])
        (id, info) = rep.items()[0]
        if info['title'] == subtask.title:
            # already exists !
            subtask_phid = id
            break
    if subtask_phid is None:
        logging.debug('\t\tCreating subtask [{}]'.format(sub.title))
        # must create it
        actions = [
                {"type" : "parent", "value" : task_phid},
                {"type": "title", "value" : sub.title}
            ]
        rep = conduit.maniphest.edit(transactions=actions)
        # TODO check rep

def main():
    init_logger()
    # wikimedia custom API
    # db = phabdb.phdb(host=config.DB_HOST,
    #                 user=config.DB_USER,
    #                 passwd=config.DB_PASS,
    #                 db="performance_schema")

    projects = kanDB.session.query(kanDB.Project).all()
    # project
    for p in projects:
        project_phid = checkProject(p)
        tasks = kanDB.session.query(kanDB.Task).filter_by(project_id=p.id)
        # task
        for t in tasks:
            task_phid = checkTask(project_phid, t)
            # add subtasks
            subtasks = kanDB.session.query(kanDB.Subtask).filter_by(task_id=t.id)
            for sub in subtasks:
                subtask_phid = checkSubtask(project_phid, task_phid, sub)


if __name__ == '__main__':
    main()
