#!/usr/bin/env python3
# coding: utf8

# sys
import os
import sys
import re
import logging
import requests
import base64
import json

# local
# from tools.wmfphablib import phabdb
import config
import kanDB
import PhabDB
from pprint import pprint

# 3rd
from phabricator.phabricator import Phabricator

# conduit API
conduit = Phabricator(host=config.CONDUIT_HOST,
                   token=config.CONDUIT_TOKEN)
conduit.update_interfaces()

# # wikimedia custom API
# db = phabdb.phdb(host=config.DB_HOST,
#                 user=config.DB_USER,
#                 passwd=config.DB_PASS,
#                 db="performance_schema")

def init_logger():
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

def checkUser(user):
    print('\t\t\t[CHECK] user [{}]'.format(user.email))
    rep = conduit.user.query(emails=[user.email])
    # TODO check owner_phid
    if not rep:
        # must create user
        print('\t\t\t[INSERT] user [{}]'.format(user.email))
        args = { 
                'username' : base64.b64encode(user.username.encode('utf-8')),
                'email' : base64.b64encode(user.email.encode('utf-8')),
                'realname' : base64.b64encode(user.name.encode('utf-8')),
                'admin' : base64.b64encode(config.PHAB_ADMIN.encode('utf-8'))
        }
        r = requests.get(config.ADD_USER_URL, params=args)
    rep = conduit.user.query(emails=[user.email])
    # we should have only one user
    info = rep[0]
    owner_phid = info['phid']
    return owner_phid

# check if a given project is present in phabricator
# if not, it will be created
def checkProject(project):
    logging.debug('[CHECK] project [{}]'.format(project.name))
    rep = conduit.project.query(names=[project.name])
    if not rep['data']:
        # must create project
        logging.debug('[INSERT] project [{}]'.format(project.name))
        # check members
        project_has_users = kanDB.session.query(kanDB.ProjectUser).filter_by(project_id=project.id)
        members_phid_list = []
        for m in project_has_users:
            user = kanDB.session.query(kanDB.User).filter_by(id=m.user_id).all()[0]
            member_phid = checkUser(user)
            members_phid_list.append(member_phid)
        rep = conduit.project.create(name=project.name, members=members_phid_list)
        # TODO check rep
    # getting phid
    rep = conduit.project.query(names=[project.name])
    project_phid = list(rep['data'].keys())[0]
    return project_phid

def checkTask(project_phid, task):
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
            user = kanDB.session.query(kanDB.User).filter_by(id=task.owner_id).all()[0]
            owner_phid = checkUser(user)
        rep = conduit.maniphest.createtask(title=task.title,
                description=task.description,
                ownerPHID=owner_phid,
                projectPHIDs=[project_phid])
        task_phid = rep['phid']
        # task inserted
        # add comments
        comments = kanDB.session.query(kanDB.Comment).filter_by(task_id=task.id)
        for c in comments:
            logging.debug('\t\t[INSERT] comment')
            # edit task to add new comment
            actions = [
                    {"type": "comment", "value" : c.comment}
                ]
            rep = conduit.maniphest.edit(transactions=actions, objectIdentifier=task_phid)
            xact = rep['transactions'][0]['phid']
            pprint(type(xact))
            xact = xact.encode('utf-8')
            # check if user exists
            author = kanDB.session.query(kanDB.User).filter_by(id=c.user_id).all()[0]
            author_phid = checkUser(author)
            # get maniphest comment object
            phab_comment = PhabDB.session.query(PhabDB.ManiphestTransactionComment).filter_by(transactionPHID=xact).all()[0]
            # update
            phab_comment.authorPHID = author_phid
            # commit
            PhabDB.session.commit()

            # TODO check rep
        # already completed ?
        if task.date_completed:
            logging.debug('Setting as closed')
            # set task as closed
            actions = [
                    {"type": "status", "value" : "RESOLVED"}
                ]
            rep = conduit.maniphest.edit(transactions=actions, objectIdentifier=task_phid)
            # TODO check rep
    return task_phid

def checkSubtask(project_phid, task_phid, subtask):
    logging.debug('\t\t[CHECK] subtask [{}]'.format(subtask.title))
    # query all subtasks of task_phid
    rep = conduit.maniphest.query(projectPHIDs=[project_phid], phids=[task_phid])
    info = list(rep.values())[0]
    task_subtask_phid_list = info['dependsOnTaskPHIDs']
    # iterate on each of these subtask
    # to see if we already exist
    subtask_phid = None
    for existing_subtask_phid in task_subtask_phid_list:
        rep = conduit.maniphest.query(phids=[existing_subtask_phid])
        id = list(rep.keys())[0]
        info = list(rep.values())[0]
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
    # author_phid = 'PHID-USER-rbqdh26r3niaff2fhk3l'
    # # get maniphest comment object
    # phab_comment = PhabDB.session.query(PhabDB.ManiphestTransactionComment).filter_by(id=248).all()[0]
    # # update
    # # phab_comment.authorPHID = author_phid
    # phab_comment.content = "test content"
    # # commit
    # PhabDB.session.flush()
    # PhabDB.session.commit()
