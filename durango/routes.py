from flask import render_template, url_for, flash, redirect
from durango import app,db,bcrypt #using bcrypt to has the passwords in user database
from durango.models import User, Task
from durango.forms import RegistrationForm, LoginForm
from flask_login import login_user,current_user,logout_user
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
    if current_user.is_authenticated:
        return redirect(url_for('home')) #redirects user to home if already logged in
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8') #returns hashed password, decode converts it from byte to string
        user=User(username=form.username.data,email=form.email.data, instituteId=form.instituteId.data,mobileNum=form.mobileNum.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Registration successful for {form.username.data}! Login now', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))  
    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Greetings '+form.username.data+'!')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account")
def account():
    return render_template('account.html',title='Account')