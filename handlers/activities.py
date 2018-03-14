import traceback
import uuid
from handlers.model.classification_model import ClassificationModel

import datetime
from flask import request, json

from handlers import APIError, _get_user
from models import db, Activity, File, Jump


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
    return json.dumps({"activity_id": activity.id}), 201


def create_activity_files(user_id, activity_id):
    data = request.get_json()

    if not data.get('stopped_at'):
        raise APIError("stopped_at is a required field", 400)

    if not data.get('rpe'):
        raise APIError("rpe is a required field", 400)

    if not data.get('files'):
        raise APIError("files is a required field", 400)

    if not len(data.get('files')) > 1:
        raise APIError("at least two files are required", 400)

    activity = _get_activity(activity_id)
    if not activity:
        raise APIError("activity does not exist", 404)

    if not activity.user_id == user_id:
        raise APIError("user is not allowed to access activity", 401)

    files = []
    response = {}

    for file_name in data.get('files'):
        file = File()
        file.id = str(uuid.uuid4())
        file.activity_id = activity_id
        file.file_name = file_name
        file.status = "upload_started"
        files.append(file)
        response[file_name] = file.id

    activity.rpe = data['rpe']
    activity.stopped_at = data['stopped_at']

    _create_activity_files(files)
    return json.dumps(response), 201


def update_activity_file_status(user_id, activity_id):
    data = request.get_json()

    if not data.get('file_name'):
        raise APIError("file_name is a required field", 400)

    if not data.get('status'):
        raise APIError("status is a required field", 400)

    if not data.get('file_uploads_remaining'):
        raise APIError("file_uploads_remaining is a required field", 400)

    file = _get_file_with_name(data.get('file_name'))
    if not file:
        raise APIError("file does not exist", 404)

    if not file.activity_id == activity_id:
        raise APIError("file does not belong to activity", 400)

    file.status = data.get('status')
    _update_activity_file()

    if not data.get('file_uploads_remaining') == 0:
        return "", 204

    activity = _get_activity(activity_id)
    files = _get_files_for_activity(activity)

    file__name_array = [file["file_name"].split("_")[0] for file in files]

    try:
        from app import model
        metrics = model.process_files(file__name_array)
    except Exception:
        traceback.print_exc()
        raise APIError("failed to process files for activity", 500)

    jumps = []
    for metric in metrics:
        jump = Jump()
        jump.id = activity.id = str(uuid.uuid4())
        jump.activity_id = activity_id
        jump.user_id = user_id
        jump.jump_date = datetime.datetime.now().strftime("%Y-%m-%d")
        jump.leg = metric["leg"]
        jump.severity = metric["severity"]
        jump.jump_time = metric["jump_time"]
        jump.abduction_angle = metric["abduction_angle"]

    _create_activity_jumps(jumps)
    return json.dumps({metrics}), 200


def get_activities(user_id):
    user = _get_user(user_id)
    if not user:
        raise APIError("invalid user", 400)

    activities = [
        {
            "activity_id": activity.id,
            "activity_type": activity.activity_type,
            "rpe": activity.rpe,
            "user_id": activity.user_id,
            "started_at": activity.started_at,
            "stopped_at": activity.stopped_at,
            "updated_at": activity.updated_at
        } for activity in _get_activities_for_user(user)
    ]
    return json.dumps({"activities": activities}), 200


def get_activity_jumps(user_id, activity_id):
    activity = _get_activity(activity_id)
    if not activity:
        raise APIError("invalid activity", 400)

    jumps = [
        {
            "jump_id": jump.id,
            "activity_id": jump.activity_id,
            "jump_time": jump.jump_time,
            "user_id": jump.user_id,
            "abduction_angle": str(jump.abduction_angle),
            "created_at": jump.created_at,
            "updated_at": jump.updated_at
        } for jump in _get_jumps_for_activity(activity)
    ]
    return json.dumps({"jumps": jumps}), 200


def _get_jumps_for_activity(activity):
    try:
        jumps = activity.jumps
    except Exception:
        traceback.print_exc()
        raise APIError("failed to fetch jumps for activity", 500)
    return jumps


def _create_activity_jumps(jumps):
    try:
        db.session.add_all(jumps)
        db.session.commit()
    except Exception:
        traceback.print_exc()
        raise APIError("failed to create new jumps", 500)


def _create_activity_files(files):
    try:
        db.session.add_all(files)
        db.session.commit()
    except Exception:
        traceback.print_exc()
        raise APIError("failed to create new files", 500)


def _get_file_with_name(file_name):
    try:
        file = db.session.query(File).filter_by(file_name=file_name).first()
    except Exception:
        traceback.print_exc()
        raise APIError("failed to fetch file", 500)
    return file


def _update_activity_file():
    try:
        db.session.commit()
    except Exception:
        traceback.print_exc()
        raise APIError("failed to update file", 500)


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


def _get_files_for_activity(activity):
    try:
        files = activity.files
    except Exception:
        traceback.print_exc()
        raise APIError("failed to fetch files for activity", 500)
    return files
