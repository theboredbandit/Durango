from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField,SelectField
from wtforms.fields.html5 import DateField,TimeField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError,Optional
from durango.models import User,Task    
class RegistrationForm(FlaskForm):
	username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])#field should not be empty and length should be between 2 and 20
	email=StringField('Email',validators=[DataRequired(),Email()])
	mobileNum=StringField('Enter your 10 digit mobile number',validators=[DataRequired(), Length(min=10,max=10,message="Mobile Number must be 10 digits long.")]) 
	instituteId=StringField('Institute Id', validators=[DataRequired()])
	password=PasswordField('Password', validators=[DataRequired(),Length(max=50)]) 
	confirm_password=PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
	app_password=PasswordField('App Password (You can leave this empty for now.)',validators=[Optional()])
	submit=SubmitField("Register")

	def validate_username(self, username):
			user=User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('Username already in use. Please choose a different one.');

	def validate_email(self, email):
			user=User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('Email already in use. Please choose a different one.');
	def validate_mobileNum(self, mobileNum):
			user=User.query.filter_by(mobileNum=mobileNum.data).first()
			if user:
				raise ValidationError('Mobile Number already in use. Please choose a different one.');
	def validate_instituteId(self, instituteId):
			user=User.query.filter_by(instituteId=instituteId.data).first()
			if user:
				raise ValidationError('Institute Id is already in use. Please choose a different one.');

class UpdateAccountForm(FlaskForm):
	username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])#field should not be empty and length should be between 2 and 20
	email=StringField('Email',validators=[DataRequired(),Email()])
	instituteId=StringField('Institute Id', validators=[DataRequired()])
	mobileNum=StringField('Mobile Number',validators=[DataRequired(), Length(min=10,max=10,message="Mobile Number must be 10 digits long.")]) 
	submit=SubmitField("Update")

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
	def validate_instituteId(self, instituteId):
		if(instituteId.data!=current_user.instituteId):
			user=User.query.filter_by(instituteId=instituteId.data).first()
			if user:
				raise ValidationError('InstituteId already in use. Please choose a different one.');
	def validate_mobileNum(self, mobileNum):
		if(mobileNum.data!=current_user.mobileNum):
			user=User.query.filter_by(mobileNum=mobileNum.data).first()
			if user:
				raise ValidationError('Mobile number already in use. Please choose a different one.');

class LoginForm(FlaskForm):
	username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])#field should not be empty and length should be between 2 and 20
	password=PasswordField('Password', validators=[DataRequired()]) 
	remember = BooleanField('Remember Me')
	submit=SubmitField("Login")

class TaskForm(FlaskForm):
	title=StringField('Title',validators=[DataRequired()])
	details=TextAreaField('Task-details')
	date=DateField('Date',validators=[DataRequired()],format='%Y-%m-%d')
	starttime=TimeField('Start Time',validators=[Optional()])
	endtime=TimeField('End Time',validators=[Optional()])
	remindtime=TimeField('Remind me at(Fill this if you want a sms reminder):',validators=[Optional()])#remindtime
	status=SelectField(
        'Status',
        choices=[('To-do', 'To-do'), ('Running', 'Running'), ('Completed', 'Completed'),('Failed','Failed')]
    )
	submit=SubmitField('Submit')


class SearchForm(FlaskForm):
	search=StringField('Enter the task-title',validators=[DataRequired()])
	submit=SubmitField('Search')

class SelectDate(FlaskForm):
	date=DateField('Date',validators=[DataRequired()],format='%Y-%m-%d')
	submit=SubmitField('GO')

class InitiateResetForm(FlaskForm):
	email=StringField('Email',validators=[DataRequired(),Email()])
	submit=SubmitField('Initiate Password Reset')
	def validate_email(self, email):
		#if(email.data!=current_user.email):
			user=User.query.filter_by(email=email.data).first()
			if user is None:
				raise ValidationError('No account associated with given email.')

class ResetPasswordForm(FlaskForm):
	password=PasswordField('Password', validators=[DataRequired(),Length(max=50)]) 
	confirmpassword=PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
	submit=SubmitField("Reset Password")

class app_passwordForm(FlaskForm):
	app_password=PasswordField('App Password', validators=[DataRequired(),Length(max=50)]) 
	submit=SubmitField("Submit")

class MessageForm(FlaskForm):
	email=StringField('Email',validators=[DataRequired(),Email()])
	message=TextAreaField('Message/Bug-description')
	submit=SubmitField("Send")

