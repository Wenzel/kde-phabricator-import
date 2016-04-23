import hashlib
import subprocess
from pprint import pprint


def get_ip(container):
    output = subprocess.check_output(["docker", "inspect", "--format", "{{ .NetworkSettings.IPAddress }}", container])
    output = output.decode('utf-8')
    output = output.strip()
    return output

KANDB_HOST = get_ip('kandb')
KANDB_USER = "root"
KANDB_PASS = "root"
KANDB_DB = "kanboard"

DB_HOST = get_ip('phabdb')
DB_PORT = "3306" # my docker container address
DB_USER = "admin"
DB_PASS = "admin"
DB_NAME = "default_maniphest"

PHAB_HOST = "http://" + get_ip('phabweb')
PHAB_ADMIN = 'admin'

SECRET_KEY = "my_secret_key"
SECRET_PATH = hashlib.sha1(SECRET_KEY.encode('utf-8')).hexdigest()

ADD_USER_URL = PHAB_HOST + ':4000' + '/' + SECRET_PATH + '/'

CONDUIT_HOST = "http://127.0.0.1:8081/api/"
CONDUIT_TOKEN = "api-vlrdlpeu4jrcoqzu46jehqkjcpoj"
