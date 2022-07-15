import time

from uuid import UUID
from datetime import datetime

from sklearn.exceptions import NotFittedError
from sklearn.utils.validation import check_is_fitted

from flask import request, g
from flask_jwt_next import current_identity

from fmexp.extensions import db, fmclassifier
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

        random_delays = False
        if 'random_delays' in request.args:
            random_delays = True if request.args['random_delays'] == 'true' else False

        advanced = False
        if 'advanced' in request.args:
            advanced = True if request.args['advanced'] == 'true' else False

        if 'bot_mode' in request.args:
            if request.args['bot_mode'] == 'request':
                new_user.bot_request_mode = '{}{}'.format(
                    'basic' if not advanced else 'advanced',
                    '_random_delays' if random_delays else '',
                )
            elif request.args['bot_mode'] == 'mouse':
                new_user.bot_mouse_mode = '{}{}'.format(
                    'basic' if not advanced else 'advanced',
                    '_random_delays' if random_delays else '',
                )

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

    if user_uuid:
        try:
            u = User.query.filter_by(uuid=UUID(user_uuid)).first()
            # fmclassifier.train_model()
            t1 = time.time()
            prediction = fmclassifier.predict(u)[0]
            t2 = time.time()
            print('PREDICTION', prediction)
            print('TIME', t2 - t1)
            response.headers['fmexp-is-bot'] = str(prediction)
            prediction = fmclassifier.predict(User.query.filter_by(uuid=UUID('20fb8e9f-4dcb-4463-b793-4e80e8b0ebd7')).first())[0]
            print('BOT PREDICTION', prediction)

        except NotFittedError:
            print('Model not fitted, skipping')

    return response
