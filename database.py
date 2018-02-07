import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Setup DB Config
db_name = os.environ.get("DB_NAME", '')
db_host = os.environ.get("DB_HOST", '')
db_user = os.environ.get("DB_USER", '')
db_password = os.environ.get("DB_PASSWORD", '')

print db_user, db_password, db_host, db_name

# Create DB Session
connection_str = 'mysql+pymysql://%s:%s@%s/%s' % (db_user, db_password, db_host, db_name)
print connection_str
engine = create_engine(connection_str, convert_unicode=True)
session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(session_maker)


def init_db():
    import models
