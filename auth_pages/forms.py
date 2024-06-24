from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email,ValidationError, EqualTo
import re


class RegisterForm(FlaskForm):

    first_name= StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name",validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired(),Email()])

    def validate_contact(form, field):
        if not re.match(r'^[0-9]+$', field.data):
            raise ValidationError('Contact should contain only numbers.')


    contact = StringField("Contact", validators=[DataRequired(), validate_contact])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit =SubmitField("Submit")
