#!/bin/bash

docker exec \
    -ti \
    phabweb \
    python3.4 /opt/kde-phabricator-import/python/server.py
