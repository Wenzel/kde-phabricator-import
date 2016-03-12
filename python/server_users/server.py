#!/usr/bin/python3

import os
import sys
import hashlib
from urllib.parse import urlparse
from urllib.parse import parse_qs
import re

import http.server
import socketserver

import process

PHABRICATOR_URI = "http://127.0.0.1/8081"
PORT = 4000
ADD_USER_PATH = "/opt/phabricator/scripts/user/add_user.php"
ARCANIST_PATH = "/opt/arcanist/bin/arc"
ARCANIST_WORKING_DIR = "/opt/arcanist/bin"
WORKING_DIR = "/opt/phabricator/scripts/user/"

SECRET_KEY = "my_secret_key"
SECRET_PATH = hashlib.sha1(SECRET_KEY.encode('utf-8')).hexdigest()

class MyHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        print(self.path)
        match = re.match(r'^/([0-9a-fA-F]+)/.*$', self.path)
        if match and match.group(1) == SECRET_PATH:
            args = parse_qs(urlparse(self.path).query)
            username = args.get('username')[0]
            email = args.get('email')[0]
            realname = args.get('realname')[0]
            admin = args.get('admin')[0]

            args = []
            args.append(ADD_USER_PATH)
            args.append(username)
            args.append(email)
            args.append(realname)
            args.append(admin)
            print('Adding {} {}'.format(username, email))
            process.run('php', args, WORKING_DIR)

def main():
    print(SECRET_PATH)
    # make sure arcanist is configured
    args = []
    args.append(ARCANIST_PATH)
    args.append('set-config')
    args.append('phabricator-uri')
    args.append(PHABRICATOR_URI)
    # test
    # process.run('php', args, ARCANIST_WORKING_DIR)

    handler = MyHandler
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("0.0.0.0", PORT), handler)
    httpd.serve_forever()

if __name__ == '__main__':
    main()
