from random import randrange
from datetime import timedelta, datetime

import json
from uuid import UUID
from urllib.parse import urlparse, urljoin

from flask import render_template, current_app, request

from fmexp.models import User


def render_template_fmexp(template_name, **kwargs):
    layout_name = current_app.config.get('LAYOUT_NAME', 'layout1')
    layout = current_app.jinja_env.get_template(f'{layout_name}.html')

    return render_template(template_name, layout=layout, **kwargs)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def json_response(data, status_code=200):
    response = current_app.response_class(json.dumps(data), mimetype='application/json')
    response.status_code = status_code

    return response


def load_cookie_user():
    user_uuid = request.cookies.get('user_uuid')
    if not user_uuid:
        return None

    return User.query.filter_by(uuid=UUID(user_uuid)).first()


def random_date():
    end = datetime.utcnow()
    start = datetime(2000, 1, 1, 0, 0, 0)
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)
