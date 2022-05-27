from flask_wtf import Form
from wtforms import StringField 
from wtforms.validators import Email, DataRequired

class CheckoutForm(Form):
    first_name = StringField('first_name', validators=[DataRequired(message='Please enter first name')])
    middle_name = StringField('middle_name')
    last_name = StringField('last_name', validators=[DataRequired(message='Please enter last name')])
    email = StringField("email", validators=[DataRequired(message="Please enter email address."), Email(message="Please enter email address.")])
    address_line_1 = StringField('address_line_1', validators=[DataRequired(message='Please enter last name')])
    address_line_2 = StringField('address_line_2')
    city = StringField('city', validators=[DataRequired(message='Please enter city')])
    state = StringField('state', validators=[DataRequired(message='Please enter state')])
    country = StringField('country', validators=[DataRequired(message='Please enter country')])
    zip_code = StringField('zip_code', validators=[DataRequired(message='Please enter zip code')])
