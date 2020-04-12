from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import DataRequired,Length,Email,EqualTo     
class RegistrationForm(FlaskForm):
	username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])#field should not be empty and length should be between 2 and 20
	email=StringField('Email',validators=[DataRequired(),Email()])
	instituteId=StringField('Institute Id', validators=[DataRequired()])
	mobileNum=StringField('Mobile Number',validators=[DataRequired(), Length(min=10,max=10,message="Mobile Number must be 10 digits long.")]) 
	password=PasswordField('Password', validators=[DataRequired(),Length(max=50)]) 
	confirm_password=PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
	submit=SubmitField("Register")

class LoginForm(FlaskForm):
	username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])#field should not be empty and length should be between 2 and 20
	#email=StringField('Email',validators=[DataRequired(),Email()])
	password=PasswordField('Password', validators=[DataRequired()]) 
	#confirm_password=PasswordField('Confirm_Password',validators=[DataRequired(), EqualTo('password')])
	remember = BooleanField('Remember Me')
	submit=SubmitField("Login")
