from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField
from wtforms.fields.html5 import DateField,TimeField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from durango.models import User,Task    
class RegistrationForm(FlaskForm):
	username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])#field should not be empty and length should be between 2 and 20
	email=StringField('Email',validators=[DataRequired(),Email()])
	instituteId=StringField('Institute Id', validators=[DataRequired()])
	mobileNum=StringField('Mobile Number',validators=[DataRequired(), Length(min=10,max=10,message="Mobile Number must be 10 digits long.")]) 
	password=PasswordField('Password', validators=[DataRequired(),Length(max=50)]) 
	confirm_password=PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
	submit=SubmitField("Register")

	def validate_username(self, username):
		if(username.data!=current_user.username):
			user=User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('Username already in use. Please choose a different one.');

	def validate_email(self, email):
		if(email.data!=current_user.email):
			user=User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('Email already in use. Please choose a different one.');
	def validate_mobileNum(self, mobileNum):
		if(mobileNum.data!=current_user.mobileNum):
			user=User.query.filter_by(mobileNum=mobileNum.data).first()
			if user:
				raise ValidationError('Mobile Number already in use. Please choose a different one.');
	def validate_instituteId(self, email):
		if(instituteId.data!=current_user.instituteId):
			user=User.query.filter_by(instituteId=instituteId.data).first()
			if user:
				raise ValidationError('Institute Id is already in use. Please choose a different one.');

class UpdateAccountForm(FlaskForm):
	username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])#field should not be empty and length should be between 2 and 20
	email=StringField('Email',validators=[DataRequired(),Email()])
	instituteId=StringField('Institute Id', validators=[DataRequired()])
	mobileNum=StringField('Mobile Number',validators=[DataRequired(), Length(min=10,max=10,message="Mobile Number must be 10 digits long.")]) 
	submit=SubmitField("Register")

	def validate_username(self, username):
		user=User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('Username already in use. Please choose a different one.');

	def validate_email(self, email):
		user=User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('Email already in use. Please choose a different one.');
	def validate_email(self, instituteId):
		user=User.query.filter_by(instituteId=instituteId.data).first()
		if user:
			raise ValidationError('InstituteId already in use. Please choose a different one.');
	def validate_email(self, email):
		user=User.query.filter_by(mobileNum=mobileNum.data).first()
		if user:
			raise ValidationError('Mobile number already in use. Please choose a different one.');

class LoginForm(FlaskForm):
	username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])#field should not be empty and length should be between 2 and 20
	#email=StringField('Email',validators=[DataRequired(),Email()])
	password=PasswordField('Password', validators=[DataRequired()]) 
	#confirm_password=PasswordField('Confirm_Password',validators=[DataRequired(), EqualTo('password')])
	remember = BooleanField('Remember Me')
	submit=SubmitField("Login")

class TaskForm(FlaskForm):
	title=StringField('Title',validators=[DataRequired()])
	details=TextAreaField('Task-details',validators=[DataRequired()])
	date=DateField('Date',validators=[DataRequired()],format='%Y-%m-%d')
	starttime=TimeField('Start Time',validators=[DataRequired()])
	endtime=TimeField('End Time',validators=[DataRequired()])
	status=StringField('Status',validators=[DataRequired()])
	submit=SubmitField('Post')