# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql.enumerated import ENUM
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Activity(Base):
    __tablename__ = 'activities'

    id = Column(String(36), primary_key=True)
    activity_type = Column(String(255), nullable=False, server_default=text("''"))
    user_id = Column(ForeignKey(u'users.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    started_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    stopped_at = Column(DateTime)
    updated_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    user = relationship(u'User')


class File(Base):
    __tablename__ = 'files'

    id = Column(String(36), primary_key=True)
    file_name = Column(String(255), nullable=False)
    file_size_mb = Column(Float(asdecimal=True), nullable=False)
    status = Column(String(255), nullable=False)
    activity_id = Column(ForeignKey(u'activities.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    activity = relationship(u'Activity')


class Jump(Base):
    __tablename__ = 'jumps'

    id = Column(String(36), primary_key=True)
    activity_id = Column(ForeignKey(u'activities.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    user_id = Column(ForeignKey(u'users.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    jump_time = Column(DateTime, nullable=False)
    abduction_angle = Column(Float(asdecimal=True), nullable=False)
    adduction_angle = Column(Float(asdecimal=True), nullable=False)
    flexion_angle = Column(Float(asdecimal=True), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    activity = relationship(u'Activity')
    user = relationship(u'User')


class User(Base):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True)
    first_name = Column(String(255), nullable=False, server_default=text("''"))
    last_name = Column(String(255), nullable=False, server_default=text("''"))
    email = Column(String(255), nullable=False, unique=True, server_default=text("''"))
    gender = Column(ENUM(u'M', u'F'))
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
