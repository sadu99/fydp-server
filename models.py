# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Action(Base):
    __tablename__ = 'actions'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(u'users.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship(u'User')


class Test(Base):
    __tablename__ = 'tests'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(u'users.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)

    user = relationship(u'User')


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    gender = Column(String(11))
    age = Column(Integer)
