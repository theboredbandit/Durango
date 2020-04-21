from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
#import flask_whooshalchemy as wa
#from celery import Celery



app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
#configuring celery for sms purpose
app.config['CELERY_BROKER_URL'] ='redis://127.0.0.1:6379/0'
app.config['CELERY_BACKEND']='redis://127.0.0.1:6379/0' #database to add asynchronous task of sending sms
#configuring whoosh for search
app.config['WHOOSH_BASE']='whoosh'
from celery import Celery

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
#celery will be used for handling the asynchronous task of sending sms reminders
celery=make_celery(app)
db=SQLAlchemy(app)
bcrypt =Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view='login' #setting the route to login
login_manager.login_message_category='info'



from durango import routes