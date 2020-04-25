from flask import render_template, url_for, flash, redirect,request,abort,jsonify,session
import requests
import json
from durango import app,db,bcrypt,celery,api,mail #using bcrypt to has the passwords in user database
from durango.models import User, Task
from durango.forms import RegistrationForm, LoginForm,UpdateAccountForm,TaskForm,SearchForm,SelectDate,ResetPasswordForm, InitiateResetForm
from flask_login import login_user,current_user,logout_user,login_required
from sqlalchemy.orm.exc import NoResultFound
from twilio.rest import Client
from datetime import datetime, timedelta
from random import sample
from durango.search import KMPSearch
import urllib.request
import urllib.parse
from flask_mail import Message
twilio_account_sid = "AC103eefd5343f4ec238f7fb6c45092d0a"
twilio_auth_token = "2de91c10b5ce9cd7e3efcec543470dec"
twilio_number = "+14784002746"

#everything here that begins with @ is a decorator
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html',db=db,User=User,Task=Task)


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    tasks=Task.query.filter_by(user_id=current_user.id).all()
    form1=SearchForm()
    form2=SelectDate()
    if form1.validate_on_submit():
        arr=[] 
        tasks2=[]
        for task in tasks:
            if KMPSearch(form1.search.data,task.title):
                arr.append(task.id)
                tasks2.append(Task.query.filter_by(id=task.id).first())
        if len(arr)==0:
            flash('Task not found!','warning')
            return redirect(url_for(dashboard))
        else:
            return render_template('search_task.html', title='Searched Task', tasks2=tasks2)
    if form2.validate_on_submit():
        return redirect(url_for('piechart',task_date=form2.date.data))
    return render_template('dashboard.html', title='Dashboard', tasks=tasks,form1=form1,form2=form2)

@app.route("/phone_verification", methods=['GET', 'POST'])
def phone_verification():
    if request.method == "POST":
        country_code = request.form.get("country_code")
        phone_number = request.form.get("phone_number")
        method = request.form.get("method")
        session['country_code'] = country_code
        session['phone_number'] = phone_number
        api.phones.verification_start(phone_number, country_code, via=method)
        return redirect(url_for("verify"))
    return render_template("phone_verification.html")

@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        token = request.form.get("token")

        phone_number = session.get("phone_number")
        country_code = session.get("country_code")

        verification = api.phones.verification_check(phone_number,
                                                     country_code,
                                                     token)

        if verification.ok():
            flash('Number verified')
            return redirect(url_for('home'))
    return render_template("verify.html")

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
            flash('Greetings '+form.username.data+'!','success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash('You have logged out  !','success')
    return redirect(url_for('home'))

@app.route("/account")
@login_required
def account():
    image_file=url_for('static',filename='profile_pics/' + current_user.image_file)
    return render_template('account.html',title='Account',image_file=image_file)


@app.route("/account/update",methods=['GET', 'POST'])
@login_required
def update_account():
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
        form.email.data=current_user.email
        form.mobileNum.data=current_user.mobileNum
        form.instituteId.data=current_user.instituteId
    image_file=url_for('static',filename='profile_pics/' + current_user.image_file)
    return render_template('update_account.html',title='Update Account',image_file=image_file,form=form,legend='Update credentials')


@app.route("/task/new",methods=['GET', 'POST'])
@login_required
def new_task():
    form=TaskForm()
    if form.validate_on_submit():
        task1=Task(title=form.title.data,date=form.date.data,starttime=form.starttime.data, endtime=form.endtime.data,details=form.details.data,remindtime=form.remindtime.data,status=form.status.data,user_id=current_user.id)
        db.session.add(task1)
        db.session.commit()  
        #for sms reminder
        if form.remindtime.data!=None:
            dt=datetime.combine(form.date.data,form.remindtime.data)
            dt=dt-timedelta(hours=5,minutes=30)
            send_sms_reminder.apply_async(args=[task1.id],eta=dt) 
             
        flash('Task created!','success')
        return redirect(url_for('dashboard'))
    return render_template('create_task.html',title='New Task',form=form, legend='Add Task')

####  code for sending sms reminder
#####################start

@celery.task()
def send_sms_reminder(task1_id):
    try:
        task1 = Task.query.filter_by(id=task1_id).first()
    except NoResultFound:
        return
    user=User.query.filter_by(id=task1.user_id).first()

    body = "Hello "+user.username+"! This is a reminder about "+task1.title+". See details at Durango."
    #twilio#client = Client(twilio_account_sid, twilio_auth_token)

    to = user.mobileNum
    #twilio#client.messages.create(to=user.mobileNum,from_=twilio_number,body=body)
    def sendSMS(apikey, numbers, message):
        data =  urllib.parse.urlencode({'apikey': apikey, 'numbers': numbers,
            'message' : message})
        data = data.encode('utf-8')
        request = urllib.request.Request("https://api.textlocal.in/send/?")
        f = urllib.request.urlopen(request, data)
        fr = f.read()
        return(fr)

    resp =  sendSMS('ujY6cl2oAUo-A7iyIcdzpXeIFQwsPzEzon8hBbGmzy', to,body)
#######################end
@app.route("/task/ <int:task_id>")
@login_required
def task(task_id):
    task=Task.query.get_or_404(task_id) #get_or_404 returns the requested page if it exists else it returns a 404 error
    return render_template('task.html',title=task.title,task=task)

@app.route("/task/ <int:task_id>/update",methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    task=Task.query.get_or_404(task_id)
    if task.user_id!=current_user.id:  # this is optional since we display only a prticular user's tasks in his dashboard
        abort(403)
    form=TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.details = form.details.data
        task.date=form.date.data
        task.starttime=form.starttime.data
        task.endtime=form.endtime.data
        task.status=form.status.data
        db.session.commit()
        flash('Task updated!', 'success')
        return redirect(url_for('task',task_id=task.id))
    elif request.method == 'GET':
        form.title.data = task.title
        form.details.data = task.details
        form.date.data=task.date
        form.starttime.data=task.starttime
        form.endtime.data=task.endtime
        form.status.data=task.status
    return render_template('create_task.html', title='Update Task',form=form, legend='Update Task')
@app.route("/task/ <int:task_id>/delete",methods=['GET', 'POST'])
@login_required
def delete_task(task_id):
    task=Task.query.get_or_404(task_id)
    if task.user_id!=current_user.id:  # this is optional since we display only a prticular user's tasks in his dashboard
        abort(403)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted!','warning')
    return redirect(url_for('dashboard'))

@app.route("/data")
@login_required
def data():
    tasks=Task.query.filter_by(user_id=current_user.id)
    to=ru=fa=co=0
    for task in tasks:
        if task.status=='To-do':
            to=to+1
        elif task.status=='Running':
            ru=ru+1
        elif task.status=='Completed':
            co=co+1
        elif task.status=='Failed':
            fa=fa+1
    values=[to,co,ru,fa]
    return jsonify({'results' : values})
@app.route("/linechart")
@login_required
def linechart():
    return render_template('linechart.html')

@app.route("/piechart/<task_date>")
@login_required
def piechart(task_date):
    tasks=Task.query.filter_by(user_id=current_user.id)
    to=ru=fa=co=0
    task_date=datetime.strptime(task_date,"%Y-%m-%d").date()
    for task in tasks:
        if task.date==task_date:
            if task.status=='To-do':
                to=to+1
            elif task.status=='Running':
                ru=ru+1
            elif task.status=='Completed':
                co=co+1
            elif task.status=='Failed':
                fa=fa+1
   
    values=json.dumps( [to, co,ru,fa] )
    return render_template('piechart.html',values=values)

def send_reset_email(user):
    token=user.get_reset_token()
    msg=Message('Password Reset Request',sender='durangoadmn@gmail.com',recipients=[user.email])
    str="Hello "+user.username+", "
    msg.body=f'''Hello {user.username}! To reset your password, visit the following link: 
{url_for('reset_token',token=token,_external=True)}
If you did not request this, please ignore the mail.
'''
    mail.send(msg)
@app.route("/reset_password",methods=['GET', 'POST'])
def reset_initiate():
    form=InitiateResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password','info')
        return redirect(url_for('login'))
    return render_template('reset_initiate.html',title='Reset Password',form=form)


@app.route("/reset_password/<token>",methods=['GET', 'POST'])
def reset_token(token):
    user=User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token.','warning')
        return redirect(url_for(reset_initiate))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8') #returns hashed password, decode converts it from byte to string
        user.password=hashed_password
        db.session.commit()
        flash(f'Password reset successful for {user.username}! Login now', 'success')
        return redirect(url_for('home'))
    return render_template('reset_token.html',title='Reset Password',form=form)