import traceback

from flask import request, json

from handlers import APIError
from models import db, Jump, Activity

from sqlalchemy import func


def get_historical_jumps(user_id):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        raise APIError("start_date and end_date are required query parameters", 400)

    jumps = [
        {"date": jump[0],
         "count": jump[1],
         "severity": jump[2],
         "abduction_angle": jump[3],
         "rpe": jump[4]
         } for jump in _get_jumps_for_user_with_id(user_id, start_date, end_date)]
    return json.dumps({"jumps": jumps}), 200


def _get_jumps_for_user_with_id(user_id, start_date, end_date):
    try:
        jumps = db.session.query(
            Jump.jump_date,
            func.count(Jump.jump_date),
            func.avg(Jump.severity),
            func.avg(Jump.abduction_angle),
            Activity.rpe
        ).join(Activity).filter(
            Jump.user_id == user_id,
            Jump.jump_date >= start_date,
            Jump.jump_date <= end_date
        ).group_by(
            Jump.jump_date,
        ).all()

        print jumps
    except Exception:
        traceback.print_exc()
        raise APIError("failed to fetch jumps for user", 500)
    return jumps
