#!/bin/bash

# run kanboard mysql db
docker run \
    -d \
    --name kandb \
    -e MYSQL_ROOT_PASSWORD="root" \
    mysql

IP=`docker inspect --format '{{ .NetworkSettings.IPAddress }}' kandb`
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

echo 'CREATE DATABASE kanboard;' > "/tmp/$$.sql"
mysql -h $IP \
    -u 'root' \
    -proot \
    < "/tmp/$$.sql"

rm -f "/tmp/$$.sql"

# insert kanboard data
mysql -h $IP \
    -u 'root' \
    -proot \
    kanboard \
    < kanboard.sql
