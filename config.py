import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_THRESHOLD = 0.25
ANGLE_CONSTANT = 0.4
JUMP_COOLDOWN = 1000
BOTH_LEGS = True

def get_db_conn_str():
    db_name = os.environ.get("DB_NAME", '')
    db_host = os.environ.get("DB_HOST", '')
    db_user = os.environ.get("DB_USER", '')
    db_password = os.environ.get("DB_PASSWORD", '')
    connection_str = 'mysql+pymysql://%s:%s@%s/%s' % (db_user, db_password, db_host, db_name)
    return connection_str


def get_test_db_conn_str():
    db_name = 'hiza-test'
    db_host = os.environ.get("DB_HOST", '')
    db_user = os.environ.get("DB_USER", '')
    db_password = os.environ.get("DB_PASSWORD", '')
    connection_str = 'mysql+pymysql://%s:%s@%s/%s' % (db_user, db_password, db_host, db_name)
    return connection_str