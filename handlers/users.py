import traceback
import uuid

from flask import request, json

from handlers import APIError
from models import db, User


def create_user():
    data = request.get_json()

    if not data.get('first_name') or not data.get('last_name'):
        raise APIError("first_name and last_name are required fields", 400)

    if not data.get('email'):
        raise APIError("email is a required field", 400)

    if not data.get('gender') or data.get('gender') not in ["M", "F"]:
        raise APIError("gender is a required field and can only be M or F", 400)

    user = User()
    user.id = str(uuid.uuid4())
    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.email = data['email']
    user.gender = data['gender']

    _create_user()
    return json.dumps({"user_id": user.id}), 200


def _create_user(user):
    try:
        db.session.add(user)
        db.session.commit()
    except Exception:
        traceback.print_exc()
        raise APIError("failed to create new user", 500)
