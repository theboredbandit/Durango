from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from kombu.utils.url import safequote
from celery import Celery

#import flask_whooshalchemy as wa


from authy.api import AuthyApiClient
from durango import config
application = Flask(__name__)


application.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
application.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
#application.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

#configuring with authy to verify phone number
application.config['AUTHY_API_KEY']='Cur6vF9dwUvuPGqDJhuaFoa7UivqYNzF'
api=AuthyApiClient(application.config['AUTHY_API_KEY'])
#configuring celery for sms purpose
#aws_access_key = safequote("AKIAJYXGSJXZWV4HPFJA")
#aws_secret_key = safequote("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")

#broker_url = "sqs://{aws_access_key}:{aws_secret_key}@".format(
 #   aws_access_key=aws_access_key, aws_secret_key=aws_secret_key,
#)

broker_transport_options = {'region': 'ap-south-1'}

#application.config['CELERY_BROKER_URL'] =broker_url
application.config.update(CELERY_BROKER_URL='sqs://sqs.ap-south-1.amazonaws.com/arn:aws:sqs:ap-south-1:788426066576:flask-es/flask-es')
application.config['CELERY_BROKER_TRANSPORT_OPTIONS']=broker_transport_options
#application.config['CELERY_BACKEND']='redis://127.0.0.1:6379/0' #database to add asynchronous task of sending sms

#setting api


def make_celery(application):
    celery = Celery(application.import_name,
                    broker=application.config['CELERY_BROKER_URL'])
    celery.conf.update(application.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with application.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
#celery will be used for handling the asynchronous task of sending sms reminders

celery=make_celery(application)
db=SQLAlchemy(application)
bcrypt =Bcrypt(application)
login_manager=LoginManager(application)
login_manager.login_view='login' #setting the route to login
login_manager.login_message_category='info'
application.config['MAIL_SERVER']='smtp.googlemail.com'
application.config['MAIL_USE_TLS']=587
application.config['MAIL_USERNAME']='durangoadmn@gmail.com'
application.config['MAIL_PASSWORD']='durango123..'
mail=Mail(application)

from durango import routes