from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
from flask_marshmallow import Marshmallow
from celery import Celery

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

def create_app(config_class=Config):
    app = Flask(__name__, static_url_path='') #static_url_path cause static
    # folder to be loaded
    app.config.from_object(config_class)

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    celery.conf.update(app.config)

    from .dbanalyst import dbanalyst
    app.register_blueprint(dbanalyst)

    return app
