import traceback
import uuid

from flask import request, json

from handlers import APIError, _get_user
from models import db, Activity


def create_activity(user_id):
    user = _get_user(user_id)
    if not user:
        raise APIError("invalid user", 400)

    data = request.get_json()
    if not data.get('activity_type'):
        raise APIError("activity_type is a required field", 400)

    activity = Activity()
    activity.id = str(uuid.uuid4())
    activity.activity_type = data['activity_type']
    activity.user_id = user_id

    _create_activity(activity)
    return json.dumps({"activity_id": activity.id}), 200


def update_activity(user_id, activity_id):
    data = request.get_json()
    if not data.get('stopped_at'):
        raise APIError("stopped_at is a required field", 400)

    activity = _get_activity(activity_id)
    if not activity:
        raise APIError("activity does not exist", 404)

    activity.stopped_at = data['stopped_at']
    _update_activity()
    return "", 204


def get_activities(user_id):
    user = _get_user(user_id)
    if not user:
        raise APIError("invalid user", 400)

    activities = [
        {
            "activity_id": activity.id,
            "activity_type": activity.activity_type,
            "user_id": activity.user_id,
            "started_at": activity.started_at,
            "stopped_at": activity.stopped_at,
            "updated_at": activity.updated_at
        } for activity in _get_activities_for_user(user)
    ]
    return json.dumps({"activities": activities}), 200


def _create_activity(activity):
    try:
        db.session.add(activity)
        db.session.commit()
    except Exception:
        traceback.print_exc()
        raise APIError("failed to create new activity", 500)


def _update_activity():
    try:
        db.session.commit()
    except Exception:
        traceback.print_exc()
        raise APIError("failed to update activity", 500)


def _get_activity(activity_id):
    try:
        activity = db.session.query(Activity).get(activity_id)
    except Exception:
        traceback.print_exc()
        raise APIError("failed to fetch user", 500)
    return activity


def _get_activities_for_user(user):
    try:
        activities = user.activities
    except Exception:
        traceback.print_exc()
        raise APIError("failed to fetch activities for user", 500)
    return activities
