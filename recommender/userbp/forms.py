from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import Email, DataRequired, Length

class LoginForm(Form):
    username = StringField("username",validators = [DataRequired(message="Please provide a username"),Length(min = 4, max = 15)])
    password = PasswordField("password", validators = [DataRequired(message="Please provide a password"),Length(min = 8, max = 80)])

class RegisterForm(Form):
    first_name = StringField("first_name",validators = [DataRequired(message ="First name required" )])
    last_name = StringField("last_name",validators = [DataRequired(message ="Last name required")])
    email = StringField("email",validators = [DataRequired(),Email(message = "Email required"),Length(max = 50)])
    phone_number = StringField("phone_number",validators = [DataRequired(message ="Phone number required")])
    country = StringField("country",validators = [DataRequired(message ="Country required")])
    username = StringField("username",validators = [DataRequired(message="Please provide a username"),Length(min = 4, max = 15)])
    password = PasswordField("password", validators = [DataRequired(message="Please provide a password"),Length(min = 8, max = 80)])



