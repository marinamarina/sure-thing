from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FloatField
from wtforms.validators import DataRequired, Email, Length, ValidationError, EqualTo
from ..models import User, Role
from .validators import validator_user_already_registered

"""This is a module holding form objects"""
class CSRFDisabledForm(Form):
    # overriding init, disabling CSRF
    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(CSRFDisabledForm, self).__init__(*args, **kwargs)

class LoginForm(CSRFDisabledForm):
    email = StringField('Email address', validators = [DataRequired(message= "Please enter your email!"), Email()])
    password = PasswordField('Password', validators=[DataRequired(message= "Please enter your password!")])
    rememberMe = BooleanField('Remember me')
    submit = SubmitField('Login')

class RegistrationForm(CSRFDisabledForm):
    email = StringField('Email', description='Email address', validators=[DataRequired(), Email(), validator_user_already_registered()])
    username = StringField('Username', description='Username', validators=[Length(1,64), validator_user_already_registered()])
    password = PasswordField('Password', description='Password', validators=[DataRequired(message= "Please enter a valid password!"), EqualTo('password2', message= "Passwords must match!" )])
    password2 = PasswordField('Confirm Password', description='Confirm Password', validators=[DataRequired(message= "Please confirm your password!")])
    submit = SubmitField('Register')

class PasswordChangeForm(CSRFDisabledForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('Password', validators=[DataRequired(), EqualTo('new_password2', message= "Passwords must match!" )])
    new_password2 = PasswordField('Re-enter Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfile(CSRFDisabledForm):
    real_name = StringField('Real name', validators=[Length(0,64)])
    location = StringField('Location', validators=[Length(0,64)])
    fav_team = StringField('Fav team', validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

class AdminManageProfiles(CSRFDisabledForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email(), validator_user_already_registered()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), validator_user_already_registered()])
    role = SelectField('Role', coerce=int)
    confirmed = BooleanField('Is confirmed?')
    real_name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(AdminManageProfiles, self).__init__()

        # generator generating a list of tuples
        self.role.choices = [(role.id, role.name) for role in Role.query.all() ]
        self.user = user


class UserDefaultPredictionSettings(CSRFDisabledForm):
    league_position_weight = StringField('League Position')
    form_weight = StringField('Form')
    home_away_weight = StringField('Home/Away')
    submit = SubmitField('Save')


class UserMatchPredictionSettings(CSRFDisabledForm):
    league_position_weight = StringField('League Position')
    form_weight = StringField('Form')
    home_away_weight = StringField('Home/Away')
    submit = SubmitField('Save')


class BlogPostForm(CSRFDisabledForm):
    title = StringField('Post title', validators=[DataRequired()])
    body_html = TextAreaField('Your post',validators=[DataRequired()])
    submit = SubmitField('Submit')

class CommentPostForm(CSRFDisabledForm):
    body_html = StringField(label='Enter your comments...', validators=[DataRequired()])
    submit = SubmitField('Submit')