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

    response = {}

    for jump in _get_jumps_for_user_with_id(user_id, start_date, end_date):

        jump_date = jump[0].strftime("%Y-%m-%d")
        if not response.get(jump_date):
            response[jump_date] = {}

        data = {"count": jump[2], "severity": jump[3], "abduction_angle": jump[4], "rpe": jump[5]}

        if not response[jump_date].get(jump[1]):
            response[jump_date][jump[1]] = data

    return json.dumps(response), 200


def _get_jumps_for_user_with_id(user_id, start_date, end_date):
    try:
        jumps = db.session.query(
            Jump.jump_date,
            Jump.leg,
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
            Jump.leg,
        ).all()
    except Exception:
        traceback.print_exc()
        raise APIError("failed to fetch jumps for user", 500)
    return jumps
