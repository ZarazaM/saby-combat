import string
from saby_combat import db
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.fields import StringField, SubmitField, BooleanField, EmailField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo
from .utils import get_user_by_username, get_user_by_email


# Custom password validator class
class Password(object):
    def __init__(self, numbers=True, uppercase=True, lowercase=True, special_characters=True):
        self.numbers = numbers
        self.uppercase = uppercase
        self.lowercase = lowercase
        self.special_characters = special_characters
        self.message = None

    def __call__(self, form, field):
        self.message = []
        if self.uppercase and not any(map(lambda x: x.isupper(), field.data)):
            self.message.append("символы верхнего регистра 'A-Z'")
        if self.lowercase and not any(map(lambda x: x.islower(), field.data)):
            self.message.append("символы нижнего регистра 'a-z'")
        if self.numbers and not any(map(lambda x: x.isdigit(), field.data)):
            self.message.append("цифры '0-9'")
        if self.special_characters and not any([1 if x in string.punctuation else 0 for x in field.data]):
            self.message.append("специальные символы")

        if self.message.__len__():
            print(self.message.__len__())
            self.message = f'Пароль должен содержать {", ".join(self.message)}.'
            raise ValidationError(self.message)
            

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    email_adress = EmailField('Email', validators=[DataRequired(), Email(check_deliverability=True)])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=30)])
    surname = StringField('Surname', validators=[DataRequired(), Length(min=2, max=30)])
    patronymic = StringField('Patronymic', validators=[Optional(), Length(min=2, max=30)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6), Password(50)])
    password_submit = PasswordField('Password_submit', validators=[EqualTo('password')])
    submit = SubmitField()

    def validate_username(form, field):
        existing_user = get_user_by_username(field.data)
        if existing_user:
            raise ValidationError(message="Пользователь с таким ником уже зарегистрирован")
        
    def validate_email_adress(form, field):
        existing_user = get_user_by_email(field.data)
        if existing_user:
            raise ValidationError(message="Пользователь с таким адресом электронной почты уже зарегистрирован")


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField()
