from models import User
from database import db_session


def get_users():
    users = db_session.query(User).all()

    for user in users:
        print user.name

    return "hi", 200
