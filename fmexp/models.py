import uuid
import json
from enum import IntEnum

from flask_scrypt import generate_random_salt, generate_password_hash, check_password_hash

from sqlalchemy.dialects.postgresql import UUID, JSONB

from fmexp.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    email = db.Column(db.String(255), nullable=True, unique=True)

    password_salt = db.Column(db.LargeBinary)
    password_hash = db.Column(db.LargeBinary)

    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)

    date_of_birth = db.Column(db.Date())

    address_line_1 = db.Column(db.String)
    address_line_2 = db.Column(db.String)
    zip_code = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    country = db.Column(db.String)

    logged_in = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def id(self):
        return str(self.uuid)

    @property
    def is_active(self):
        return self.email is not None

    def set_password(self, password):
        self.password_salt = generate_random_salt()
        self.password_hash = generate_password_hash(password, self.password_salt)

    def check_password(self, password):
        if not password:
            return False

        return check_password_hash(password, self.password_hash, self.password_salt)

    def get_json(self):
        data = {}
        for attr in [
            'email',
            'first_name',
            'last_name',
            'date_of_birth',
            'address_line_1',
            'address_line_2',
            'zip_code',
            'city',
            'state',
            'country',
        ]:
            data[attr] = str(getattr(self, attr))

        return data


class DataPointDataType(IntEnum):
    REQUEST = 1
    MOUSE = 2

class DataPoint(db.Model):
    __tablename__ = 'data_points'

    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.DateTime, nullable=False)

    user_uuid = db.Column(UUID(as_uuid=True), db.ForeignKey('users.uuid'), nullable=False)
    user = db.relationship('User', backref='datapoints')

    data_type = db.Column(db.Integer, nullable=False, default=DataPointDataType.REQUEST.value)

    data = db.Column(JSONB)

    def __init__(self, created, user_uuid, data_type, data):
        self.created = created
        self.user_uuid = user_uuid
        self.data_type = data_type
        self.data = data
