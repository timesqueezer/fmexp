from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    EmailField,
    BooleanField,
    DateField,
    StringField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    ValidationError,
    Optional,
)

from fmexp.models import User


class UserLoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])


class UserRegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), Length(min=8)])
    not_robot = BooleanField('I am not a robot ;)', validators=[DataRequired()])

    def validate_email(form, field):
        existing_user = User.query.filter_by(email=field.data).first()
        if existing_user:
            raise ValidationError('Email already exists')

    def validate_password2(form, field):
        if field.data != form.password.data:
            raise ValidationError('Passwords do not match')


class UserProfileForm(FlaskForm):
    email = EmailField('Email', validators=[Email(), Optional()])
    first_name = StringField('First Name', validators=[Optional()])
    last_name = StringField('Last Name', validators=[Optional()])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    address_line_1 = StringField('Address Line 1', validators=[Optional()])
    address_line_2 = StringField('Address Line 2', validators=[Optional()])
    zip_code = StringField('Postal Code', validators=[Optional()])
    city = StringField('City', validators=[Optional()])
    state = StringField('State', validators=[Optional()])
    country = StringField('Country', validators=[Optional()])


class UserChangePasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), Length(min=8)])

    def validate_password2(form, field):
        if field.data != form.password.data:
            raise ValidationError('Passwords do not match')
