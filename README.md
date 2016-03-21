# kde-phabricator-import
Scripts to import data from services used by the KDE community into Phabricator

# requirements

- Docker
- Python 3
- virtualenv

# setup



export your data from kanboard database into a file named `kanboard.sql` and
place it at the root of the repo.

- run `git submodule update --init`
- run `./setup_kanboard.sh` to setup kanboard mysql database
- run `./setup_phabricator.sh` to setup phabricator database and web application
- go to http://127.0.0.1:8081 and setup the phabricator admin account
- then generate a new CONDUIT API token and replace the value in `config.py`
- run `./run_server.sh` to run the server in phabricator web container
- check the configuration in `config.py`
- run `./python/test.py` to start the import
