#!/bin/bash

# run phabricator mysql container
docker run \
    -d \
    --name phabdb \
    yesnault/docker-phabricator-mysql

IP=`docker inspect --format '{{ .NetworkSettings.IPAddress }}' phabdb`
# wait for db to be ready
echo 'wait for mysql container to be ready'
ready="false"
while [ $ready == "false" ]; do
    echo '' | nc $IP 3306
    if [ $? -eq 0 ]; then
        ready="true"
    else
        sleep 1
    fi
done

# build phabricator web
cd docker-phabricator && docker build -t phabricator .

# run phabricator
docker run \
    -d \
    --name phabweb \
    -p 127.0.0.1:8081:80 \
    --link phabdb:database \
    phabricator

docker exec \
    -ti \
    phabweb \
    git clone https://github.com/Wenzel/kde-phabricator-import
