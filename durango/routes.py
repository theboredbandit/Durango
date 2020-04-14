from flask import render_template, url_for, flash, redirect,request
from durango import app,db,bcrypt #using bcrypt to has the passwords in user database
from durango.models import User, Task
from durango.forms import RegistrationForm, LoginForm,UpdateAccountForm,TaskForm
from flask_login import login_user,current_user,logout_user,login_required

#everything here that begins with @ is a decorator
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/dashboard")
def dashboard():
    tasks=Task.query.all()
    return render_template('dashboard.html', title='Dashboard', tasks=tasks)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard')) #redirects user to dashboard if already logged in; function name is passed in url_for
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
        return redirect(url_for('dashboard'))  
    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            next_page=request.args.get('next')#looks for queries in request; args is a dictionary; we use get and not directly use 'next' as key to return the value because key might be empty leading to an error. get, in that case would fetch a none
            flash('Greetings '+form.username.data+'!')
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account")
@login_required
def account():
    form=UpdateAccountForm()
    if form.validate_on_submit():
       # hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8') #returns hashed password, decode converts it from byte to string
        current_user.username=form.username.data
        current_user.email=form.email.data
        current_user.instituteId=form.instituteId.data
        current_user.mobileNum=form.mobileNum.data  
        #db.session.add(user)
        db.session.commit()
        flash(f'Account updated successfully', 'success') #success is bootstrap class for the alert
        return redirect(url_for('account'))
    elif request.method=='GET':  #if submit btn is not clicked and account page is requested, it eill already fill the usename field with existing data
        form.username.data=current_user.username

    image_file=url_for('static',filename='profile_pics/' + current_user.image_file)
    return render_template('account.html',title='Account',image_file=image_file)

@app.route("/task/new",methods=['GET', 'POST'])
@login_required
def new_task():
    form=TaskForm()
    if form.validate_on_submit():
        task=Task(title=form.title.data,date=form.date.data,time=form.time.data, details=form.details.data,status=form.status.data,user_id=current_user.id)
        db.session.add(task)
        db.session.commit()        
        flash('Task created!','success')
        return redirect(url_for('dashboard'))
    return render_template('create_task.html',title='New Task',form=form)