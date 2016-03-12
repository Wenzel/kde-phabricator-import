import hashlib

KANDB_HOST = "172.17.0.4"
KANDB_USER = "root"
KANDB_PASS = "admin"
KANDB_DB = "kanboard"

DB_HOST = "172.17.0.2" # my docker container address
DB_PORT = "3306" # my docker container address
DB_USER = "admin"
DB_PASS = "admin"
DB_NAME = "default_project"

SECRET_KEY = "my_secret_key"
SECRET_PATH = hashlib.sha1(SECRET_KEY.encode('utf-8')).hexdigest()
PHAB_HOST = 'http://172.17.0.3:4000/'
PHAB_SECRET_URL = PHAB_HOST + SECRET_PATH + '/'
PHAB_ADMIN = 'admin'

CONDUIT_HOST = "http://127.0.0.1:8081/api/"
CONDUIT_TOKEN = "api-txmxzqtgwfxgcgeoiru4aidamcy2"
