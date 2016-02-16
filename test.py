#!/usr/bin/env python

# sys
import os
import sys
import re
import pdb

# local
import config

# 3rd
from phabricator import Phabricator
from tools.wmfphablib import phabdb

def main():
    db = phabdb.phdb(host=config.DB_HOST,
                    user=config.DB_USER,
                    passwd=config.DB_PASS,
                    db="performance_schema")

    phab = Phabricator(host=config.CONDUIT_HOST,
                       token=config.CONDUIT_TOKEN)
    phab.update_interfaces()
    phab.user.whoami()


if __name__ == '__main__':
    main()
