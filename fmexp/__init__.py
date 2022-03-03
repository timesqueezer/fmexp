import os

# import click
from flask import Flask

from fmexp.extensions import (
    db,
    migrate,
    jwt,
)
import fmexp.login
import fmexp.request_logger


def create_app(
    additional_config=None,
    instance_path=os.getenv('FMEXP_INSTANCE_PATH'),
):
    app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)

    app.config.from_object('fmexp.config')
    app.config.from_pyfile('fmexp.conf', silent=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from fmexp.main import main
    app.register_blueprint(main)

    @app.cli.command('create-tables')
    def create_tables():
        db.create_all()

    return app
