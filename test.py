#!/usr/bin/env python

# sys
import os
import sys
import re
import pdb

# local
from tools.wmfphablib import phabdb
import config
from kanboardDB import engine, Task, Subtask, Project, User, Column

# 3rd
from phabricator import Phabricator
from sqlalchemy.orm import sessionmaker



def main():
    db = phabdb.phdb(host=config.DB_HOST,
                    user=config.DB_USER,
                    passwd=config.DB_PASS,
                    db="performance_schema")

    phab = Phabricator(host=config.CONDUIT_HOST,
                       token=config.CONDUIT_TOKEN)
    # phab.update_interfaces()
    # phab.maniphest.createtask(title="title",
    #                          description="full desc")


    # create session
    Session = sessionmaker(bind=engine)
    session = Session()

    # queries
    tasks = session.query(Task).all()
    for t in tasks:
        print("Task {} : {}".format(t.id, t.title))



if __name__ == '__main__':
    main()
