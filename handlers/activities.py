import traceback
import uuid
from sets import Set

import datetime
from flask import request, json
from operator import itemgetter

from handlers import APIError, _get_user
from handlers.model.classification_model import model
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

    if not int(data.get('file_uploads_remaining')) == 0:
        return "", 204

    activity = _get_activity(activity_id)
    files = _get_files_for_activity(activity)

    file_name_array = [file.file_name.split("_")[0] for file in files]
    file_name_set = Set(file_name_array)

    jumps = []

    for file_name in file_name_set:
        try:
            metrics = model.process_file(file_name)
        except Exception:
            traceback.print_exc()
            raise APIError("failed to process files for activity", 500)

        for metric in metrics:
            jump = Jump()
            jump.id = str(uuid.uuid4())
            jump.activity_id = activity_id
            jump.user_id = user_id
            jump.jump_date = datetime.datetime.now().strftime("%Y-%m-%d")
            jump.leg = metric["leg"]
            jump.severity = float(metric["severity"])
            jump.jump_time = int(metric["jump_time"])
            jump.abduction_angle = float(metric["abduction_angle"])
            jumps.append(jump)

    _create_activity_jumps(jumps)
    return "activity successfully processed", 200


def get_activities(user_id):
    user = _get_user(user_id)
    if not user:
        raise APIError("invalid user", 400)

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        activities = _get_activities_for_user(user)
    else:
        activities = _get_activities_for_user_between_dates(user, start_date, end_date)

    response = [
        {
            "activity_id": activity.id,
            "activity_type": activity.activity_type,
            "rpe": activity.rpe,
            "user_id": activity.user_id,
            "started_at": activity.started_at,
            "stopped_at": activity.stopped_at,
            "updated_at": activity.updated_at
        } for activity in activities
    ]

    sorted_activities = sorted(response, key=itemgetter('started_at'), reverse=True)
    return json.dumps({"activities": sorted_activities}), 200


def get_daily_activity_time(user_id):
    user = _get_user(user_id)
    if not user:
        raise APIError("invalid user", 400)

    return json.dumps({"time": str(_get_daily_activity_time(user))}), 200


def get_activity_jumps(user_id, activity_id):
    activity = _get_activity(activity_id)
    if not activity:
        raise APIError("invalid activity", 400)

    response = {}

    for jump in _get_jumps_for_activity(activity):

        if not response.get(jump.jump_time):
            response[jump.jump_time] = {}

        data = {"severity": str(jump.severity), "abduction_angle": str(jump.abduction_angle)}

        if not response[jump.jump_time].get(jump.leg):
            response[jump.jump_time][jump.leg] = data

    return json.dumps(response), 200


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


def _get_activities_for_user_between_dates(user, start_date, end_date):
    try:
        activities = db.session.query(Activity).filter(
            Activity.user_id == user.id,
            Activity.started_at >= start_date,
            Activity.started_at <= end_date
        ).all()
    except Exception:
        traceback.print_exc()
        raise APIError("failed to fetch activities between dates for user", 500)
    return activities


def _get_files_for_activity(activity):
    try:
        files = activity.files
    except Exception:
        traceback.print_exc()
        raise APIError("failed to fetch files for activity", 500)
    return files


def _get_daily_activity_time(user):
    try:
        start_date = datetime.datetime.utcnow().date()
        end_date = datetime.datetime.utcnow().date() + datetime.timedelta(days=1)

        result = db.engine.execute("select sum(updated_at - started_at) from activities where started_at >='%s' "
                                   "and started_at <= '%s' and user_id='%s'" % (start_date, end_date, user.id))

        for row in result:
            time = row[0]

    except Exception:
        traceback.print_exc()
        raise APIError("failed to fetch daily activity time for user", 500)
    return time
