from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from kombu.utils.url import safequote
from celery import Celery

#import flask_whooshalchemy as wa


from authy.api import AuthyApiClient


application = Flask(__name__)


application.config['SECRET_KEY'] = 'XXXXXXXXXXXXXXXXXXX'
application.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
#application.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

#configuring with authy to verify phone number

application.config['AUTHY_API_KEY']='XXXXXXXXXXXXXXXXXX'
api=AuthyApiClient(application.config['AUTHY_API_KEY'])
#configuring celery for sms purpose


broker_transport_options = {'region': 'ap-south-1'}

#application.config['CELERY_BROKER_URL'] =broker_url
application.config.update(CELERY_BROKER_URL='sqs://sqs.ap-south-1.amazonaws.com/arn:aws:sqs:ap-south-1:788426066576:flask-es/flask-es')
application.config['CELERY_BROKER_TRANSPORT_OPTIONS']=broker_transport_options


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
socketio = SocketIO(application)
login_manager=LoginManager(application)
login_manager.login_view='login' #setting the route to login
login_manager.login_message_category='info'
application.config['MAIL_SERVER']='smtp.googlemail.com'
application.config['MAIL_USE_TLS']=587
application.config['MAIL_USERNAME']='durangoadmn@gmail.com'
application.config['MAIL_PASSWORD']='durango123..'
mail=Mail(application)

from durango import routes
