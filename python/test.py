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


def init_logger():
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)


def main():
    init_logger()
    # wikimedia custom API
    # db = phabdb.phdb(host=config.DB_HOST,
    #                 user=config.DB_USER,
    #                 passwd=config.DB_PASS,
    #                 db="performance_schema")

    # conduit API
    conduit = Phabricator(host=config.CONDUIT_HOST,
                       token=config.CONDUIT_TOKEN)
    conduit.update_interfaces()


    logging.debug('Getting all projects from Kanboard')
    projects = kanDB.session.query(kanDB.Project).all()
    # project
    for p in projects:
        logging.debug('Checking for project {}'.format(p.name))
        rep = conduit.project.query(names=[p.name])
        if not rep['data']:
            logging.debug('Creating project {}'.format(p.name))
            rep = conduit.project.create(name=p.name, members=[])
            # TODO check rep
        # getting phid
        rep = conduit.project.query(names=[p.name])
        (phid, info) = rep['data'].items()[0]
        logging.debug('Project PHID {}'.format(phid))
        logging.debug('Getting all project tasks') 
        tasks = kanDB.session.query(kanDB.Task).filter_by(project_id=p.id)
        # task
        for t in tasks:
            logging.debug('Searching for task {}'.format(t.title))
            rep = conduit.maniphest.query(projectPHIDs=[phid])
            task_phid = None
            task_subtasks_phids = []
            for key, value in rep.items():
                if value['title'] == t.title:
                    task_phid = key
                    task_subtasks_phids = value['dependsOnTaskPHIDs']
                    break
            if task_phid is None:
                # must create task
                logging.debug('Creating task {}'.format(t.title))
                rep = conduit.maniphest.createtask(title=t.title,
                        description=t.description,
                        projectPHIDs=[phid])
                task_phid = rep['phid']
            # add subtasks
            subtasks = kanDB.session.query(kanDB.Subtask).filter_by(task_id=t.id)
            for sub in subtasks:
                # already exists ?
                logging.debug('Searching for subtask {}'.format(sub.title))
                subtask_phid = None
                for i in task_subtasks_phids:
                    rep = conduit.maniphest.query(phids=[i])
                    if rep:
                        key = rep.keys()[0]
                        val = rep[key]
                        if val['title'] == sub.title:
                            logging.debug('found subtask')
                            subtask_phid = i
                            break
                if subtask_phid is None:
                    logging.debug('creating subtask')
                    # must create subtask
                    actions = [
                            {"type" : "parent", "value" : task_phid},
                            {"type": "title", "value" : sub.title}
                        ]
                    rep = conduit.maniphest.edit(transactions=actions)


if __name__ == '__main__':
    main()
