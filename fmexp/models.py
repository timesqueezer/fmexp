import uuid
import json

from itertools import groupby

from enum import IntEnum
from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

from flask_scrypt import generate_random_salt, generate_password_hash, check_password_hash

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import aliased

from fmexp.extensions import db
from fmexp.utils import (
    fast_query_count,
    fast_query_count_q,
)


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
    bot_request_mode = db.Column(db.String, nullable=True) # 'basic', 'basic_random_delays', 'advanced', 'advanced_random_delays'
    bot_mouse_mode = db.Column(db.String, nullable=True) # 'basic', 'basic_random_delays', 'advanced', 'advanced_random_delays'

    @staticmethod
    def query_filtered(threshold=2, data_type=None):

        data_point_count_q = (
            db.session.query(
                db.func.count(DataPoint.id)
            )
            .filter(DataPoint.user_uuid == User.uuid)
        )

        if data_type:
            # data_point_alias = aliased(DataPoint)
            data_point_count_q = data_point_count_q.filter(DataPoint.data_type == data_type)

        q = User.query.filter(
            data_point_count_q.as_scalar() > threshold
        )

        return q

    @property
    def id(self):
        return str(self.uuid)

    @property
    def is_active(self):
        return self.email is not None

    @hybrid_property
    def datapoint_count(self):
        return (
            db.session.query(
                db.func.count(DataPoint.id)
            )
            .filter(DataPoint.user_uuid == self.uuid)
            .as_scalar()
        )

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

    def get_mouse_action_chains(self):
        ACTION_MAX_LENGTH = 2 # seconds
        SAMPLE_RATE = 30 # 1/s
        SAMPLE_TD_US = 1000_000 / SAMPLE_RATE # microseconds

        mouse_data_point_q = (
            DataPoint
            .query
            .filter_by(
                user_uuid=self.uuid,
                data_type=DataPointDataType.MOUSE.value,
            )
            # .order_by(DataPoint.id)
        )

        """first_dp = mouse_data_point_q.first()
        width = first_dp.data['screen']['width']
        height = first_dp.data['screen']['height']"""

        action_chains = []
        current_chain = []
        current_chain_first_dp = None
        last_dp = None
        last_td = 0

        dps_per_width = {}
        for width, l in groupby(
            sorted(mouse_data_point_q, key=lambda dp: dp.data['screen']['width']),
            lambda dp: dp.data['screen']['width'],
        ):
            dps_per_width[width] = list(l)

        for width, dps in dps_per_width.items():
            sorted_dps = sorted(dps, key=lambda dp: dp.id)

            first_dp = sorted_dps[0]

            for i, dp in enumerate(sorted_dps):
                td = 0

                if last_dp and abs(dp.created - last_dp.created) < timedelta(microseconds=SAMPLE_TD_US):
                    td = last_td + timedelta(microseconds=SAMPLE_TD_US)

                elif current_chain_first_dp is not None:
                    td = dp.created - current_chain_first_dp.created

                else:
                    td = timedelta(microseconds=0)

                last_td = td

                rel_x = dp.data['position']['x'] - first_dp.data['position']['x']
                rel_y = dp.data['position']['y'] - first_dp.data['position']['y']

                dp_data = (
                    rel_x,
                    rel_y,
                    0 if dp.data['type'] == 'move' else 1,
                    td.microseconds / 1000,
                )

                if len(current_chain) == 0:
                    current_chain_first_dp = dp

                last_dp = dp

                current_chain.append(dp_data)

                if dp.data['type'] != 'move' or td > timedelta(seconds=ACTION_MAX_LENGTH):
                    action_chains.append(current_chain)
                    current_chain = []
                    current_chain_first_dp = None
                    last_dp = None
                    last_td = 0

        return {
            'action_chains': action_chains,
            # 'width': width,
            # 'height': height,
        }

    def get_mouse_features(self):
        MIN_ACTIONS = 4

        mouse_ac_data = self.get_mouse_action_chains()

        ac_features = []

        for ac in mouse_ac_data['action_chains']:
            if len(ac) < MIN_ACTIONS:
                continue

            x = np.array([a[0] for a in ac])
            y = np.array([a[1] for a in ac])
            t = np.array([a[3] for a in ac])

            # first phase: preprocessing

            # distance to start
            s = np.array([
                sum(
                    np.sqrt(
                        ((x[k + 1] - x[k]) ** 2) +
                        ((y[k + 1] - y[k]) ** 2)
                    )
                    for k in range(i)
                ) for i, _ in enumerate(x)
            ])

            # TODO: linear + cubic spline interpolation
            # https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.CubicSpline.html

            axis_points = np.arange(0, max(t), 1)

            x_lin_interp = np.interp(axis_points, t, x)
            y_lin_interp = np.interp(axis_points, t, y)

            # cs_x = CubicSpline(t, x)
            # cs_y = CubicSpline(t, y)


            # spatial information
            x_prime = x_lin_interp
            y_prime = y_lin_interp
            # x_prime = cs_x(axis_points)
            # y_prime = cs_y(axis_points)

            s_prime = np.array([
                sum(
                    np.sqrt(
                        ((x_prime[k + 1] - x_prime[k]) ** 2) +
                        ((y_prime[k + 1] - y_prime[k]) ** 2)
                    )
                    for k in range(i)
                ) for i, _ in enumerate(x_prime)
            ])

            theta = [0]
            theta.extend([
                np.arctan2(
                    (y_prime[k + 1] - y_prime[k]),
                    (x_prime[k + 1] - x_prime[k])
                )
                for k in range(len(y_prime) - 1)
            ])

            # todo: curvature and maybe use equation from paper

            """fig, ax = plt.subplots()
            # ax.plot(t, x, 'o', label='x')
            # ax.plot(t, y, 'o', label='y')
            # ax.plot(t, s, label='s')
            # ax.plot(axis_points, x_lin_interp, label='x lin interp')
            # ax.plot(axis_points, y_lin_interp, label='y lin interp')
            # ax.plot(axis_points, cs_x(axis_points), label='x cubic interp')
            # ax.plot(axis_points, cs_y(axis_points), label='y interp')


            # ax.plot(axis_points, x_prime, label='x\'')
            # ax.plot(axis_points, y_prime, label='y\'')
            ax.plot(axis_points, theta, label='theta')

            ax.legend()
            plt.show()"""

            # temporal information
            # dt = k / len(x)
            len_x = len(x)

            v_x = [0]
            v_x.extend([
                (x[k] - x[k - 1]) / (k / len_x)
                for k in range(1, len_x)
            ])

            v_y = [0]
            v_y.extend([
                (y[k] - y[k - 1]) / (k / len_x)
                for k in range(1, len(y))
            ])

            v = [
                np.sqrt(v_x[k]**2 + v_y[k]**2)
                for k in range(len(v_x))
            ]

            # acceleration
            a = [0]
            a.extend([
                (v[k] - v[k - 1]) / (k / len_x)
                for k in range(1, len(v))
            ])

            # jerk
            j = [0]
            j.extend([
                (a[k] - a[k - 1]) / (k / len_x)
                for k in range(1, len(a))
            ])

            # angular velocity
            w = [0]
            w.extend([
                theta[k] - theta[k - 1] / (k / len_x)
                for k in range(1, len(theta))
            ])

            # statistical analysis for actual feature data
            features = []

            """for _v in vector:
                for measure in minimum, maximum, mean, standard deviation, and (maximum - minimum)."""

            # for vector in [x_prime, y_prime, theta, curvature, delta_curvature, v_x, v_y, v, a, j, w]
            for vector in [x_prime, y_prime, theta, v_x, v_y, v, a, j, w]:
                for measure in [np.min, np.max, np.mean, np.std, 'max-min']:
                    if measure == 'max-min':
                        features.append(np.max(vector) - np.min(vector))

                    else:
                        features.append(measure(vector))

            # t_n: time of stroke
            # s_n-1: length of stroke
            t_n = t[-1] - t[0]
            s_n_1 = s[-1]

            features.append(t_n)
            features.append(s_n_1)

            # straightness
            straightness = np.sqrt(
                ( (x[0] - x[-1]) ** 2 ) +
                ( (y[0] - y[-1]) ** 2 )
            ) / max(s_n_1, 1)

            features.append(straightness)

            # jitter: ratio between original and smoothed path lengths
            jitter = s[-1] / max(s_prime[-1], 1)

            features.append(jitter)

            # TODO: number of "critical points" which have high curvature
            # TODO: time to click
            # TODO: number of pauses
            # TODO: paused time
            # TODO: paused time ratio

            ac_features.append(features)

        return ac_features


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

    user_uuid = db.Column(UUID(as_uuid=True), db.ForeignKey('users.uuid'), nullable=False, index=True)
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
