from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_next import JWT


db = SQLAlchemy()
migrate = Migrate()
jwt = JWT()
