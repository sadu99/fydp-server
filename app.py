#!/usr/bin/env python

from flask import Flask, jsonify

import config
from handlers import users, activities, APIError, health
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.get_db_conn_str()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.debug = True

# Initialize DB
db.init_app(app)

# Initialize Routes

# Health
app.add_url_rule('/health', view_func=health.monitor, methods=["GET"])

# Users
app.add_url_rule('/users', view_func=users.create_user, methods=["POST"])

# Activities
app.add_url_rule('/users/<user_id>/activities', view_func=activities.get_activities, methods=["GET"])
app.add_url_rule('/users/<user_id>/activities', view_func=activities.create_activity, methods=["POST"])
app.add_url_rule('/users/<user_id>/activities/<activity_id>', view_func=activities.update_activity, methods=["PUT"])


@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    app.run()
