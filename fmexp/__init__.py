import os

# import click
from flask import Flask

import fmexp.login
import fmexp.request_logger
from fmexp.extensions import (
    db,
    migrate,
    jwt,
    fmclassifier,
)
from fmexp.models import User


def create_app(
    additional_config=None,
    instance_path=os.getenv('FMEXP_INSTANCE_PATH'),
):
    app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)

    app.config.from_object('fmexp.config')
    app.config.from_pyfile('fmexp.conf', silent=True)

    if additional_config:
        app.config.from_object(additional_config)

    if os.getenv('FLASK_ADDITIONAL_CONFIG'):
        app.config.from_object(os.getenv('FLASK_ADDITIONAL_CONFIG'))

    print('additional_config', additional_config)
    print('SQLALCHEMY_DATABASE_URI', app.config['SQLALCHEMY_DATABASE_URI'])

    """from pprint import pprint
    pprint(app.config)"""

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from fmexp.main import main
    app.register_blueprint(main)

    @app.cli.command('create-tables')
    def create_tables():
        db.create_all()

    """with app.app_context():
        fmclassifier.load_data()
        fmclassifier.train_model()
        print('Model trained')"""

    return app
