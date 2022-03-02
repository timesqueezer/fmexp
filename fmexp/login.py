import json
from uuid import UUID

from flask import (
    request,
    abort,
    redirect,
    url_for,
)
from flask_jwt_next import JWTError, current_identity, jwt_required

from fmexp.extensions import jwt, db
from fmexp.forms import (
    UserLoginForm,
    UserRegisterForm,
)
from fmexp.models import User
from fmexp.main import main
from fmexp.utils import (
    render_template_fmexp,
    is_safe_url,
    json_response,
    load_cookie_user,
)


@jwt.authentication_handler
def authenticate(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        user.logged_in = True
        db.session.commit()
        return user


@jwt.identity_handler
def identity(payload):
    return User.query.filter_by(uuid=UUID(payload['identity'])).first()


@jwt.auth_response_handler
def auth_response_handler(access_token, identity):
    return json.dumps({ 'token': access_token })


@main.route('/register', methods=['POST'])
def register():
    user = load_cookie_user()
    if user and user.is_active:
        return json_response(user.get_json())

    form = UserRegisterForm()
    if form.validate_on_submit():
        user.email = form.email.data
        user.set_password(form.password.data)

        db.session.commit()

        return json_response(user.get_json())

    return json_response({
        'errors': form.errors,
        'form_errors': form.form_errors,
    }, 400)


@main.route('/content/register', methods=['GET'])
def register_content():
    form = UserRegisterForm()
    return render_template_fmexp('register.html', form=form)


"""@main.route('/login', methods=['POST'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email).first()

        next_url = request.args.get('next')

        if not is_safe_url(next_url):
            return abort(400)"""


@main.route('/content/login', methods=['GET'])
def login_content():
    form = UserLoginForm()
    return render_template_fmexp('login.html', form=form)
