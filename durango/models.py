from datetime import datetime
from durango import db,login_manager;
from flask_login import UserMixin
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
    image_file=db.Column(db.String(20),nullable=False,default='default.jpg')
    password=db.Column(db.String(50),nullable=False)
    tasks=db.relationship('Task',backref='author',lazy=True)
    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.instituteId}','{self.mobileNum}','{self.image_file}')"

class Task(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100), nullable=False)
    date=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    details=db.Column(db.Text,nullable=False)
    status=db.Column(db.String(20),nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)

    def __repr__(self):
        return f"Task('{self.title}','{self.date}','{self.status}')"
