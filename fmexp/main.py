import os
import uuid
import random

# from dateutil.parser import parse
from datetime import datetime

from faker import Faker

from flask import Blueprint, send_file, request, abort
from flask_jwt_next import current_identity, jwt_required

from fmexp.extensions import db, fmclassifier
from fmexp.forms import (
    UserProfileForm,
    UserChangePasswordForm,
)
from fmexp.models import (
    DataPoint,
    User,
    DataPointDataType,
    DataPointUserType,
)
from fmexp.stats import get_stats
from fmexp.utils import (
    render_template_fmexp,
    json_response,
    random_date,
)


main = Blueprint('main', __name__, template_folder='templates', static_folder='static')

fake = Faker()


@main.route('/')
@main.route('/<path:path>')
def index(path=None):
    return render_template_fmexp('index.html')


@main.route('/data-capture', methods=['POST'])
def data_capture():
    payload = request.get_json()

    if not payload.get('meta') or not payload['meta'].get('user_uuid'):
        abort(400)

    if current_identity and \
        str(current_identity.uuid) != payload['meta']['user_uuid']:
        abort(400)

    for dp in payload['data']:
        created = datetime.utcnow()

        user_type = DataPointUserType.BOT.value if request.cookies.get('fmexp_bot') else DataPointUserType.HUMAN.value

        new_datapoint = DataPoint(
            created,
            payload['meta']['user_uuid'],
            DataPointDataType.MOUSE.value,
            user_type,
            dp['data'],
        )
        db.session.add(new_datapoint)

    db.session.commit()

    return '', 200


@main.route('/content/blog')
def blog():
    return render_template_fmexp('blog.html', fake=fake, random=random, random_date=random_date)


@main.route('/content/blog-entry/<path:path>')
def blog_entry(path=None):
    return render_template_fmexp('blog_entry.html', fake=fake, random=random, random_date=random_date)


@main.route('/content/home')
def home():
    return render_template_fmexp('home.html')


@main.route('/content/contact')
def contact():
    return render_template_fmexp('contact.html')


@main.route('/content/profile')
@jwt_required()
def profile():
    user_profile_form = UserProfileForm(obj=current_identity)
    user_change_password_form = UserChangePasswordForm(obj=current_identity)
    return render_template_fmexp(
        'profile.html',
        user_profile_form=user_profile_form,
        user_change_password_form=user_change_password_form,
    )


@main.route('/user', methods=['GET', 'POST'])
@jwt_required()
def user():
    if request.method == 'GET':
        if not current_identity or not current_identity.is_active:
            abort(400)

        return json_response(current_identity.to_dict())

    elif request.method == 'POST':
        user_profile_form = UserProfileForm()
        if user_profile_form.validate_on_submit():
            user_profile_form.populate_obj(current_identity)
            db.session.commit()

            return json_response(current_identity.to_dict())

        return json_response({
            'errors': user_profile_form.errors,
            'form_errors': user_profile_form.form_errors,
        }, 400)


@main.route('/password', methods=['POST'])
@jwt_required()
def password():
    user_change_password_form = UserChangePasswordForm()
    if user_change_password_form.validate_on_submit():
        current_identity.set_password(user_change_password_form.password.data)
        db.session.commit()

        return '', 204

    return json_response({
        'errors': user_change_password_form.errors,
        'form_errors': user_change_password_form.form_errors,
    }, 400)


@main.route('/content/admin')
@jwt_required()
def admin():
    if current_identity.email != 'matzradloff@gmail.com':
        abort(401)

    stats = get_stats()

    return render_template_fmexp('admin.html', stats=stats)


@main.route('/admin/train-model', methods=['POST'])
@jwt_required()
def admin_train_model():
    if current_identity.email != 'matzradloff@gmail.com':
        abort(401)

    fmclassifier.load_data()
    fmclassifier.train_model()

    return '', 204


@main.route('/dist')
@main.route('/dist/<path:path>')
def webpack_dist(path=None):
    return send_file(os.path.join('templates/frontend/dist/', path))
