from flask_wtf import FlaskForm
from wtforms import StringField, TextField, PasswordField, validators
from wtforms.validators import DataRequired, Email


class RegistrationForm(FlaskForm):
    # username = StringField('Username', validators=[DataRequired()])
    username = StringField(
        'Username', [validators.DataRequired(), validators.Length(min=4, max=20)])
    email = TextField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             [validators.DataRequired(),
                              validators.Length(min=8, max=20),
                              validators.EqualTo(
                                  'confirm', message='Passwords must match')
                              ]
                             )
    confirm = PasswordField('Confirm Password')

class EmailForm(FlaskForm):
    email = TextField('Email', validators=[DataRequired(), Email()])


class PasswordForm(FlaskForm):
    password = PasswordField('Password',
                             [validators.DataRequired(),
                              validators.Length(min=8, max=20),
                              validators.EqualTo(
                                  'confirm', message='Passwords must match')
                              ]
                             )
    confirm = PasswordField('Confirm Password')
