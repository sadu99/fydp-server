import traceback

from models import User, db


class APIError(Exception):
    def __init__(self, message, status_code, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def _get_user(user_id):
    try:
        user = db.session.query(User).get(user_id)
    except Exception:
        traceback.print_exc()
        raise APIError("failed to fetch user", 500)
    return user
