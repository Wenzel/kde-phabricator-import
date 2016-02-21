#!/usr/bin/env python

# sys
import os
import sys
import re
import logging
import pdb

# local
# from tools.wmfphablib import phabdb
import config
import kanDB
import PhabDB
import pprint

# 3rd
from phabricator import Phabricator


def init_logger():
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)


def main():
    init_logger()
    # db = phabdb.phdb(host=config.DB_HOST,
    #                 user=config.DB_USER,
    #                 passwd=config.DB_PASS,
    #                 db="performance_schema")

    # conduit API
    phab = Phabricator(host=config.CONDUIT_HOST,
                       token=config.CONDUIT_TOKEN)
    phab.update_interfaces()


    logging.debug('Getting all projects from Kanboard')
    projects = kanDB.session.query(kanDB.Project).all()
    # project
    for p in projects:
        logging.debug('Searching for project {}'.format(p.name))
        rep = phab.project.query(names=[p.name])
        if not rep['data']:
            logging.debug('Creating project {}'.format(p.name))
            rep = phab.project.create(name=p.name, members=[])
        else:
            (phid, info) = rep['data'].items()[0]
            logging.debug('found {}'.format(phid))
        logging.debug('Getting all project tasks') 
        tasks = kanDB.session.query(kanDB.Task).filter_by(project_id=p.id)
        # task
        for t in tasks:
            logging.debug('Searching for task {}'.format(t.title))

if __name__ == '__main__':
    main()
