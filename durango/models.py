from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from durango import db,login_manager,application
from flask_login import UserMixin

import arrow;

#decorator for login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) #getting user by id


class User(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20),unique=True, nullable=False)
    email=db.Column(db.String(100),unique=True, nullable=False)
    instituteId=db.Column(db.String(20), unique=True, nullable=False)
    mobileNum=db.Column(db.String(10), unique=True, nullable=False)
    image_file=db.Column(db.String(20),nullable=False,default='user.png')
    password=db.Column(db.String(50),nullable=False)
    app_password=db.Column(db.String(50),nullable=True)
    tasks=db.relationship('Task',backref='author',lazy=True)
 
    def get_reset_token(self,expires_sec=1800):
        s=Serializer(application.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    @staticmethod #not accepting a self parameter as an argument    
    def verify_reset_token(token):
        s=Serializer(application.config['SECRET_KEY'])
        #adding a try catch block since the token might expire before the function executes
        try:
            user_id=s.loads(token)['user_id']

        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.instituteId}','{self.mobileNum}','{self.image_file}')"

class Task(db.Model):
    ##__searchable__=['title','details']

    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100), nullable=False)
    date=db.Column(db.Date(),nullable=False)
    starttime=db.Column(db.Time,nullable=True)
    endtime=db.Column(db.Time,nullable=True)
    remindtime=db.Column(db.Time,nullable=True)#remindtime
    details=db.Column(db.Text,nullable=True)
    status=db.Column(db.String(20),nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    message_id=db.Column(db.Text,nullable=True)

    def __repr__(self):
        return f"Task('{self.title}','{self.date}','{self.starttime}','{self.endtime}',{self.status}')"

class m_ids(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    removed_id=db.Column(db.Text,nullable=True)

    def __repr__(self):
        return f"m_ids('{self.id}','{self.removed_id}')"
