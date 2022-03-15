import uuid
import json

from enum import IntEnum
from datetime import datetime

from flask_scrypt import generate_random_salt, generate_password_hash, check_password_hash

from sqlalchemy.dialects.postgresql import UUID, JSONB

from fmexp.extensions import db
from fmexp.utils import fast_query_count


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

    is_bot = db.Column(db.Boolean, nullable=False, default=False)

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

    def to_dict(self):
        data = {}
        for attr in [
            'uuid',
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
            d = getattr(self, attr)
            data[attr] = str(d) if d else d

        return data

    def get_accumulated_request_features(self):
        data = []

        request_data_point_q = DataPoint.query.filter_by(
            user_uuid=self.uuid,
            data_type=DataPointDataType.REQUEST.value,
        )

        total_count = fast_query_count(request_data_point_q)

        # Feature 1: 4xx percentage
        http_400_count = fast_query_count(
            request_data_point_q.filter(
                DataPoint.data[('response', 'status_code')].as_integer().between(400, 500)
            )
        )
        data.append(http_400_count / total_count)

        # Feature 2: css percentage
        css_count = fast_query_count(
            request_data_point_q.filter(DataPoint.data[('response', 'content_type')].astext == 'text/css; charset=utf-8')
        )
        data.append(css_count / total_count)

        # Feature 3: js percentage
        js_count = fast_query_count(
            request_data_point_q.filter(DataPoint.data['response']['content_type'].astext == 'application/javascript; charset=utf-8')
        )
        data.append(js_count / total_count)

        # Feature 4: requests with previous requested url as part
        previous_count = 0
        previous_dp_url = None
        for dp in request_data_point_q.order_by(DataPoint.created):
            if previous_dp_url and previous_dp_url in dp.data['request']['path']:
                previous_count += 1

            previous_dp_url = dp.data['request']['path']

        data.append(previous_count / total_count)

        # Feature 5: time between first and last request in session
        first_dp = request_data_point_q.order_by(DataPoint.created).first()
        last_dp = request_data_point_q.order_by(DataPoint.created.desc()).first()
        data.append((last_dp.created - first_dp.created).seconds)

        return data


class DataPointDataType(IntEnum):
    REQUEST = 1
    MOUSE = 2


class DataPointUserType(IntEnum):
    HUMAN = 1
    BOT = 2

class DataPoint(db.Model):
    __tablename__ = 'data_points'

    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.DateTime, nullable=False)

    user_uuid = db.Column(UUID(as_uuid=True), db.ForeignKey('users.uuid'), nullable=False)
    user = db.relationship('User', backref='datapoints')

    data_type = db.Column(db.Integer, nullable=False, default=DataPointDataType.REQUEST.value)
    user_type = db.Column(db.Integer, nullable=False, default=DataPointUserType.HUMAN.value)

    data = db.Column(JSONB)

    def __init__(self, created, user_uuid, data_type, user_type, data):
        self.created = created
        self.user_uuid = user_uuid
        self.data_type = data_type
        self.user_type = user_type
        self.data = data

    def to_dict(self):
        data = {}
        data['created'] = datetime.timestamp(self.created)
        data['user_type'] = self.user_type

        if self.data_type == DataPointDataType.REQUEST.value:
            for k, v in self.data['request'].items():
                if k == 'origin' or not v:
                    continue

                data['request_' + k] = v

        return data
