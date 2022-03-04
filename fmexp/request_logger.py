
from datetime import datetime

from flask import request, g

from fmexp.extensions import db
from fmexp.main import main
from fmexp.models import (
    DataPoint,
    User,
    DataPointDataType,
    DataPointUserType,
)


@main.after_request
def fmexp_after_request(response):
    if '/admin' in request.url:
        return response

    user_uuid = request.cookies.get('user_uuid')

    is_bot = bool(request.cookies.get('fmexp_bot')) or request.args.get('fmexp_bot')

    if not user_uuid:
        new_user = User()
        if is_bot:
            new_user.is_bot = True

        db.session.add(new_user)
        db.session.commit()

        user_uuid = str(new_user.uuid)

        response.set_cookie('user_uuid', user_uuid)

    data = {
        'request': {},
        'response': {},
        'meta': {
            'user_uuid': user_uuid,
        },
    }
    data['request']['method'] = request.method
    data['request']['url'] = request.url
    data['request']['path'] = request.path
    data['request']['origin'] = request.origin
    data['request']['remote_addr'] = request.remote_addr
    data['request']['referrer'] = request.referrer

    data['response']['content_type'] = response.content_type
    data['response']['content_length'] = response.content_length
    data['response']['date'] = str(response.date)
    data['response']['status_code'] = response.status_code

    user_type = DataPointUserType.BOT.value if is_bot else DataPointUserType.HUMAN.value

    dp = DataPoint(
        datetime.utcnow(),
        user_uuid,
        DataPointDataType.REQUEST.value,
        user_type,
        data,
    )
    db.session.add(dp)
    db.session.commit()

    return response
