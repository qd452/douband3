#!/usr/bin/env python
# coding: utf-8
from flask_script import Manager
from app import create_app, db
from app.models import User, Movie, UserCollection
from flask_migrate import Migrate, MigrateCommand
import pandas as pd
from datetime import datetime


app = create_app()

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def create_db():
    """Create database for """
    db.create_all()


@manager.option('-u', '--name', dest='name', default='foo')
def create_user(name):
    u = User(name)
    db.session.add(u)
    db.session.commit()


@manager.option('-c', '--csvfile', dest='csv')
def add_movies_batch(csv):
    df = pd.read_csv(csv)
    df['url'] = df['mv_url'].apply(lambda x: x.rsplit('/', 2)[1])
    mvlst = df.to_dict('records')
    # https://stackoverflow.com/questions/26141183/insert-a-list-of-dictionary-using-sqlalchemy-efficiently
    conn = db.engine.connect()
    # https://stackoverflow.com/questions/30316913/bulk-inserts-with-flask-sqlalchemy
    conn.execute(Movie.__table__.insert(), mvlst)


if __name__ == '__main__':
    manager.run()
