from wtforms import Form
from wtforms import StringField, TextField, TextAreaField, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms import PasswordField

from wtforms import validators

class TransactionForm(Form):
    desusername = StringField('Usuario Destino',
    [
    validators.Required(message='El usuario es requerido!.'),
    validators.length(min=4, max=50, message='ingrese un usuario valido!.')
    ])
    valor = IntegerField('Valor',
    [
    validators.Required(message='El valor es requerido!.')
    ])

    otp = IntegerField('OTP',
    [
    validators.Required(message='El valor es requerido!.')
    ])

class LoginForm(Form):
    username = StringField('Usuario',
    [
    validators.Required(message='El usuario es requerido!.'),
    validators.length(min=4, max=50, message='ingrese un usuario valido!.')
    ])
    password = PasswordField('Password',
    [
    validators.Required(message='El password es requerido!.')
    ])

class RegisterForm(Form):
    username = StringField('Usuario',
    [
    validators.Required(message='El usuario es requerido!.'),
    validators.length(min=4, max=25, message='ingrese un usuario valido!.')
    ])
    email = EmailField('Correo Electronico',
    [
    validators.Required(message='El correo es requerido!.'),
    validators.Email(message='ingrese un correo valido!.'),
    validators.length(min=4, max=50, message='ingrese un email valido!.')
    ])
    password = PasswordField('Password',
    [
    validators.Required(message='El password es requerido!.'),
    validators.EqualTo('confirm', message='Password debe coincidir.')
    ])
    confirm = PasswordField('Repeat Password')
