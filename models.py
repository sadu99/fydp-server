# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.String(36), primary_key=True)
    activity_type = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue())
    user_id = db.Column(db.ForeignKey(u'users.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    started_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    stopped_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    rpe = db.Column(db.Integer)

    user = db.relationship(u'User', primaryjoin='Activity.user_id == User.id', backref=u'activities')


class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.String(36), primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    activity_id = db.Column(db.ForeignKey(u'activities.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

    activity = db.relationship(u'Activity', primaryjoin='File.activity_id == Activity.id', backref=u'files')


class Jump(db.Model):
    __tablename__ = 'jumps'

    id = db.Column(db.String(36), primary_key=True)
    activity_id = db.Column(db.ForeignKey(u'activities.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.ForeignKey(u'users.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    jump_time = db.Column(db.DateTime, nullable=False)
    abduction_angle = db.Column(db.Float(asdecimal=True), nullable=False)
    adduction_angle = db.Column(db.Float(asdecimal=True), nullable=False)
    flexion_angle = db.Column(db.Float(asdecimal=True), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

    activity = db.relationship(u'Activity', primaryjoin='Jump.activity_id == Activity.id', backref=u'jumps')
    user = db.relationship(u'User', primaryjoin='Jump.user_id == User.id', backref=u'jumps')


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True)
    first_name = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue())
    last_name = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue())
    email = db.Column(db.String(255), nullable=False, unique=True, server_default=db.FetchedValue())
    gender = db.Column(db.String(2), nullable=False, server_default=db.FetchedValue())
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
