#!/usr/bin/env python
# coding: utf8

# sys
import os
import sys
import re
import logging
import requests

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

def checkUser(user):
    rep = conduit.user.query(emails=[user.email])
    # TODO check owner_phid
    if not rep:
        # must create user
        print('[INSERT] user [{}]'.format(user.email))
        args { 
                'username' : user.username,
                'email' : user.email,
                'realname' : user.name,
                'admin' : config.PHAB_ADMIN
        }
        r = requests.get(config.PHAB_SECRET_URL, params=args)
    rep = conduit.user.query(emails=[user.email])
    # we should have only one user
    (id, info) = rep.items()[0]
    owner_phid = info['phid']
    return owner_phid

# check if a given project is present in phabricator
# if not, it will be created
def checkProject(project):
    # utf8
    project.name = project.name.decode('utf-8', 'ignore')
    logging.debug('[CHECK] project [{}]'.format(project.name))
    rep = conduit.project.query(names=[project.name])
    if not rep['data']:
        logging.debug('[INSERT] project [{}]'.format(project.name))
        rep = conduit.project.create(name=project.name, members=[])
        # TODO check rep
    # getting phid
    rep = conduit.project.query(names=[project.name])
    (project_phid, info) = rep['data'].items()[0]
    return project_phid

def checkTask(project_phid, task):
    # must transform task.title and task.description from str to unicode for comparison
    # also remove non utf8 characters TODO how to keep them ?
    task.title = task.title.decode('utf-8', 'ignore')
    task.description = task.description.decode('utf-8', 'ignore')
    logging.debug('\t[CHECK] task [{}]'.format(task.title))
    rep = conduit.maniphest.query(projectPHIDs=[project_phid])
    task_phid = None
    for key, value in rep.items():
        if value['title'] == task.title:
            task_phid = key
            break
    if task_phid is None:
        # must create task
        logging.debug('\t[INSERT] task [{}]'.format(task.title))
        # check if this task has been assigned to someone
        owner_phid = None
        if task.owner_id != 0:
            # find user in kanDB
            user = kanDB.session.query(kanDB.User).filter_by(id=task.owner_id)
            owner_phid = checkUser(user)
        rep = conduit.maniphest.createtask(title=task.title,
                description=task.description,
                ownerPHID=owner_phid,
                projectPHIDs=[project_phid])
        task_phid = rep['phid']
    return task_phid

def checkSubtask(project_phid, task_phid, subtask):
    # check utf8
    subtask.title = subtask.title.decode('utf-8', 'ignore')
    logging.debug('\t\t[CHECK] subtask [{}]'.format(subtask.title))
    # query all subtasks of task_phid
    rep = conduit.maniphest.query(projectPHIDs=[project_phid], phids=[task_phid])
    (id, info) = rep.items()[0]
    task_subtask_phid_list = info['dependsOnTaskPHIDs']
    # iterate on each of these subtask
    # to see if we already exist
    subtask_phid = None
    for existing_subtask_phid in task_subtask_phid_list:
        rep = conduit.maniphest.query(phids=[existing_subtask_phid])
        (id, info) = rep.items()[0]
        if info['title'] == subtask.title:
            # already exists !
            subtask_phid = id
            break
    if subtask_phid is None:
        logging.debug('\t\t[INSERT] subtask [{}]'.format(subtask.title))
        # must create it
        actions = [
                {"type" : "parent", "value" : task_phid},
                {"type": "title", "value" : subtask.title},
                {"type": "projects.set", "value" : [project_phid]}
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
            if task_phid:
                # add subtasks
                subtasks = kanDB.session.query(kanDB.Subtask).filter_by(task_id=t.id)
                for sub in subtasks:
                    subtask_phid = checkSubtask(project_phid, task_phid, sub)


if __name__ == '__main__':
    main()
