#!/usr/bin/env python3
import os

basedir = os.path.abspath(os.path.dirname(__file__))
env = os.environ.get('WEBAPP_ENV')


class Config:
    os.environ.get('SECRET_KEY') or 'any complex string'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
