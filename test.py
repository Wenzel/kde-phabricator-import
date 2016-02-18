#!/usr/bin/env python

# sys
import os
import sys
import re
import pdb

# local
from tools.wmfphablib import phabdb
import config
from kanboard import Kanboard

# 3rd
from phabricator import Phabricator
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, Table
from sqlalchemy.orm import sessionmaker


# global
engine = create_engine('sqlite:///db.sqlite', echo=True)
Base = declarative_base(engine)

class Task(Base):
    __tablename__ = 'tasks'
    __table_args__ = {'autoload':True}

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
        print(t.title)



if __name__ == '__main__':
    main()
