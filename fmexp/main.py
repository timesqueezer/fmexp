import os
import uuid

from dateutil.parser import parse

from flask import Blueprint, send_file, request, abort
from flask_jwt_next import current_identity, jwt_required

from fmexp.extensions import db
from fmexp.forms import (
    UserProfileForm,
    UserChangePasswordForm,
)
from fmexp.models import DataPoint, User
from fmexp.utils import (
    render_template_fmexp,
    json_response,
)


main = Blueprint('main', __name__, template_folder='templates', static_folder='static')


@main.route('/')
@main.route('/<path:path>')
def index(path=None):
    return render_template_fmexp('index.html')


@main.route('/user-uuid', methods=['POST'])
def user_uuid():
    if current_identity:
        return { 'user_uuid': str(current_identity.uuid) }

    already_set_uuid = request.cookies.get('user_uuid')
    if already_set_uuid:
        return { 'user_uuid': already_set_uuid }

    # new_user_uuid = uuid.uuid4()
    new_user = User()
    db.session.add(new_user)
    db.session.commit()

    new_user_uuid = new_user.uuid

    return { 'user_uuid': str(new_user_uuid) }


@main.route('/data-capture', methods=['POST'])
def data_capture():
    payload = request.get_json()

    if not payload.get('meta') or not payload['meta'].get('user_uuid'):
        abort(400)

    if current_identity and \
        str(current_identity.uuid) != payload['meta']['user_uuid']:
        abort(400)

    for dp in payload['data']:
        created = parse(dp['dt'])

        new_datapoint = DataPoint(created, payload['meta']['user_uuid'], dp['data'])
        db.session.add(new_datapoint)

    db.session.commit()

    return '', 200


@main.route('/content/blog')
def blog():
    return render_template_fmexp('blog.html')


@main.route('/content/home')
def home():
    return render_template_fmexp('home.html')


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

        return json_response(current_identity.get_json())

    elif request.method == 'POST':
        user_profile_form = UserProfileForm()
        if user_profile_form.validate_on_submit():
            user_profile_form.populate_obj(current_identity)
            db.session.commit()

            return json_response(current_identity.get_json())

        return json_response({
            'errors': user_profile_form.errors,
            'form_errors': user_profile_form.form_errors,
        }, 400)


@main.route('/dist')
@main.route('/dist/<path:path>')
def webpack_dist(path=None):
    return send_file(os.path.join('templates/frontend/dist/', path))
