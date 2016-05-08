#!/usr/bin/env python
# coding: utf8

# sys
import os
import sys
import re
import logging
import requests
import base64
import json
import time

# local
import kanDB

# 3rd
from phabricator.phabricator import Phabricator

# conduit API
conduit = Phabricator(host='https://phabricator.kde.org/api/',
                   token='<token-here>')
conduit.update_interfaces()

def checkUser(user):
    print('[CHECK] user [{}]'.format(user.email))
    rep = conduit.user.query(emails=[user.email])
    return rep

def main():
    list_user_without_accounts = []
    list_user = kanDB.session.query(kanDB.User).all()
    for u in list_user:
        present = checkUser(u)
        if not present:
            print('Missing in phabricator')
            list_user_without_accounts.append(u)
            
    with open('missing.txt', 'w') as f:
        for user in list_user_without_accounts:
            f.write(user.email)
            f.write('\n')


if __name__ == '__main__':
    main()
