from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
db=SQLAlchemy(app)

class User(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	username=db.Column(db.String(20),unique=True, nullable=False)
	email=db.Column(db.String(100),unique=True, nullable=False)
	instituteId=db.Column(db.String(20), unique=True, nullable=False)
	mobileNum=db.Column(db.String(10), unique=True, nullable=False)
	image_file=db.Column(db.String(20),nullable=False,default='default.jpg')
	password=db.Column(db.String(50),nullable=False)
	tasks=db.relationship('Task',backref='author',lazy=True)
	def __repr__(self):
		return f"User('{self.username}','{self.email}','{self.image_file}')"

class Task(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	title=db.Column(db.String(100), nullable=False)
	date=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
	details=db.Column(db.Text,nullable=False)
	status=db.Column(db.String(20),nullable=False)
	user_id=db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)

	def __repr__(self):
		return f"Task('{self.title}','{self.date}','{self.status}')"

tasks = [
    {
        'title': 'hall event',
        'details': 'opensoft meeting',
        'date': 'April 20, 2018',
        'time': '9.00 pm-12.00 am',
        'status':'Done'
        
    },
    {
        'title': 'programming contest',
        'details': 'codechef cookoff',
        'date': 'April 21, 2018',
      	'time': '8.00 pm-10.30pm',
      	'status':'To-do'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', tasks=tasks)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == 'theboredbandit' and form.password.data == 'abc123':
            flash('Welcome '+form.username.data+'!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(debug=True)