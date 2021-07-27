from flask import render_template, url_for, flash, redirect,request,abort,jsonify,session
import requests
import json
import imaplib
from durango import application,db,bcrypt,celery,api,mail,socketio #using bcrypt to has the passwords in user database
from durango.models import User, Task,m_ids,Connection
from durango.forms import RegistrationForm, LoginForm,UpdateAccountForm,TaskForm,SearchForm,SelectDate,ResetPasswordForm, InitiateResetForm, app_passwordForm,MessageForm
from durango.connections import is_connection_or_pending, get_connection_requests, get_connections
from flask_login import login_user,current_user,logout_user,login_required
from sqlalchemy.orm.exc import NoResultFound
from twilio.rest import Client
from datetime import datetime, timedelta
from random import sample
from durango.search import KMPSearch
from durango.mail import readmail
import urllib.request
import urllib.parse
from flask_mail import Message


#everything here that begins with @ is a decorator
@application.route("/")
@application.route("/home")
def home():
    return render_template('home.html',db=db,User=User,Task=Task)


@application.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    tasks=Task.query.filter_by(user_id=current_user.id).all()
    tasks.reverse()
    form1=SearchForm()
    form2=SelectDate()
    if form1.validate_on_submit():
        arr=[] 
        tasks2=[]
        for task in tasks:
            a=form1.search.data
            b=task.title
            if KMPSearch(a.casefold(),b.casefold()):
                arr.append(task.id)
                tasks2.append(Task.query.filter_by(id=task.id).first())
        if len(arr)==0:
            flash('Task not found!','warning')
            return redirect(url_for('dashboard'))
        else:
            data=json.dumps(form1.search.data)
            return render_template('search_task.html', title='Searched Task', tasks2=tasks2,data=data)
    if form2.validate_on_submit():
        return redirect(url_for('piechart',task_date=form2.date.data))
    return render_template('dashboard.html', title='Dashboard', tasks=tasks,form1=form1,form2=form2)

@application.route("/phone_verification", methods=['GET', 'POST'])
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

@application.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        token = request.form.get("token")

        phone_number = session.get("phone_number")
        country_code = session.get("country_code")

        verification = api.phones.verification_check(phone_number,
                                                     country_code,
                                                     token)
        user=User.query.filter_by(mobileNum=phone_number).first()
        if verification.ok():

            flash('Registration successful for '+user.username+' ! Login now.','success')
            return redirect(url_for('login'))
        else:
            if user:
                db.session.delete(user)
                db.session.commit()
            flash('Invalid OTP!','danger')
    return render_template("verify.html")

@application.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already a user!','info')
        return redirect(url_for('dashboard')) #redirects user to dashboard if already logged in; function name is passed in url_for
    form = RegistrationForm()
    if form.validate_on_submit():

        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8') #returns hashed password, decode converts it from byte to string
        #if app_password field is not-empty
        user=User(username=form.username.data,email=form.email.data, instituteId=form.instituteId.data,mobileNum=form.mobileNum.data,password=hashed_password)

        db.session.add(user)
        db.session.commit()
        flash(f'You are almost there.(Please do not click back button.)', 'success')
        return render_template("phone_verification.html",pn=user.mobileNum)
    return render_template('register.html', title='Register', form=form)

@application.route("/login", methods=['GET', 'POST'])
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

@application.route("/logout")
def logout():
    logout_user()
    flash('You have logged out  !','success')
    return redirect(url_for('home'))

@application.route("/account")
@login_required
def account():
    image_file=url_for('static',filename='images/user.png')
    return render_template('account.html',title='Account',image_file=image_file)

@application.route("/phone_verification_update", methods=['GET', 'POST'])
def phone_verification_update():
    if request.method == "POST":
        country_code = request.form.get("country_code")
        phone_number = request.form.get("phone_number")
        method = request.form.get("method")
        session['country_code'] = country_code
        session['phone_number'] = phone_number
        api.phones.verification_start(phone_number, country_code, via=method)
        return redirect(url_for("verify_update"))
    return render_template("phone_verification_update.html")


@application.route("/verify_update", methods=["GET", "POST"])
def verify_update():
    if request.method == "POST":
        token = request.form.get("token")
        phone_number = session.get("phone_number")
        country_code = session.get("country_code")
        verification = api.phones.verification_check(phone_number,
                                                     country_code,
                                                     token)
        if verification.ok():
            current_user.mobileNum=phone_number
            db.session.commit()
            flash('Account updated successfully!','success')
            return redirect(url_for('account'))
        else:
            flash('Invalid OTP!','danger')
    return render_template("verify_update.html")

@application.route("/account/update",methods=['GET', 'POST'])
@login_required
def update_account():
    form=UpdateAccountForm()
    if form.validate_on_submit():
       # hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8') #returns hashed password, decode converts it from byte to string
        current_user.username=form.username.data
        current_user.email=form.email.data
        current_user.instituteId=form.instituteId.data
        db.session.commit()
        #db.session.add(user)
        if form.mobileNum.data != current_user.mobileNum:
            return render_template("phone_verification_update.html",pn=form.mobileNum.data)
        else:
            flash('Account updated successfully!','success')
            return redirect(url_for('account'))
    elif request.method=='GET':  #if submit btn is not clicked and account page is requested, it eill already fill the usename field with existing data
        form.username.data=current_user.username
        form.email.data=current_user.email
        form.mobileNum.data=current_user.mobileNum
        form.instituteId.data=current_user.instituteId
    image_file=url_for('static',filename='profile_pics/' + current_user.image_file)
    return render_template('update_account.html',title='Update Account',image_file=image_file,form=form,legend='Update credentials')

@application.route("/account/delete",methods=['GET', 'POST'])
@login_required
def delete_account():
    user=User.query.filter_by(id=current_user.id).first()
    tasks=Task.query.filter_by(user_id=current_user.id).all()
    for task in tasks:
        db.session.delete(task)
    connection=Connection.query.filter_by(user_a_id=current_user.id).all()
    for c in connection:
        db.session.delete(c)
    connection=Connection.query.filter_by(user_b_id=current_user.id).all()
    for c in connection:
        db.session.delete(c)
    db.session.commit()
    db.session.delete(user)
    db.session.commit()
    flash('Account deleted','success')
    return redirect(url_for('home'))

@application.route("/task/new",methods=['GET', 'POST'])
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

@celery.task(name='tasks.send_sms_reminder')
def send_sms_reminder(task1_id):
    try:
        task1 = Task.query.filter_by(id=task1_id).first()
    except NoResultFound:
        return
    user=User.query.filter_by(id=task1.user_id).first()

    body = "Hello "+user.username+"! This is a reminder about "+task1.title+". See details at Durango."
    #twilio#client = Client(twilio_account_sid, twilio_auth_token)

    to =user.mobileNum
    #twilio#client.messages.create(to=user.mobileNum,from_=twilio_number,body=body)
    URL = 'https://www.sms4india.com/api/v1/sendCampaign'

    def sendPostRequest(reqUrl, apiKey, secretKey, useType, phoneNo, senderId, textMessage):     
      req_params = {
      'apikey':'GHAV00PT4TX58WKEJPVQGESYMHB3JKSO',
      'secret':'R73HSSKN8UJ1NYKL',
      'usetype':'stage',
      'phone': to,
      'message':body,
      'senderid':'SMSIND'
      }
      return requests.post(reqUrl, req_params)

    # get response
    response = sendPostRequest(URL, 'provided-api-key', 'provided-secret', 'prod/stage', 'valid-to-mobile', 'active-sender-id', 'message-text' )
#######################end
@application.route("/task/ <int:task_id>")
@login_required
def task(task_id):
    task=Task.query.get_or_404(task_id) #get_or_404 returns the requested page if it exists else it returns a 404 error
    return render_template('task.html',title=task.title,task=task)

@application.route("/task/ <int:task_id>/update",methods=['GET', 'POST'])
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
@application.route("/task/ <int:task_id>/delete",methods=['GET', 'POST'])
@login_required
def delete_task(task_id):
    task=Task.query.get_or_404(task_id)
    if task.user_id!=current_user.id:  # this is optional since we display only a prticular user's tasks in his dashboard
        abort(403)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted!','warning')
    return redirect(url_for('dashboard'))

@application.route("/data")
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
@application.route("/linechart")
@login_required
def linechart():
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
    return render_template('linechart.html',to=to,ru=ru,co=co,fa=fa,total=to+ru+co+fa)

@application.route("/piechart/<task_date>")
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
    return render_template('piechart.html',values=values,date=task_date)

def send_reset_email(user):
    token=user.get_reset_token()
    msg=Message('Password Reset Request',sender='durangoadmn@gmail.com',recipients=[user.email])
    str="Hello "+user.username+", "
    msg.body=f'''Hello {user.username}! To reset your password, visit the following link: 
{url_for('reset_token',token=token,_external=True)}
If you did not request this, please ignore the mail.
'''
    mail.send(msg)
@application.route("/reset_password",methods=['GET', 'POST'])
def reset_initiate():
    form=InitiateResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password','info')
        return redirect(url_for('login'))
    return render_template('reset_initiate.html',title='Reset Password',form=form)


@application.route("/reset_password/<token>",methods=['GET', 'POST'])
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


@application.route("/mail_tasks",methods=['GET', 'POST'])
@login_required
def mail_tasks():
    if current_user.app_password==None:
        form=app_passwordForm()
        if form.validate_on_submit():
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            username = current_user.email
            password = form.app_password.data
            try:
                mail.login(username, password)
            except mail.error as e:
                if 'Invalid credentials' in str(e):
                    flash('Incorrect App password!','danger')
                    return render_template('app_password.html',form=form)
            current_user.app_password=form.app_password.data
            db.session.commit()
            flash('App password added successfully','success')
            return redirect(url_for('mail_tasks'))
        return render_template('app_password.html',form=form)
    else:
        msgs=readmail(current_user.email,current_user.app_password)
        temp=[]
        for msg in msgs:
            if Task.query.filter_by(message_id=msg[4]).first():
                continue
            temp.append(msg)
        return render_template('mail_tasks.html',msgs=temp)


@application.route("/mail_task_add/<message_id>/<subject>",methods=['GET', 'POST'])
@login_required
def mail_task_add(message_id,subject):
    form=TaskForm()
    t=message_id
    if form.validate_on_submit():
        task=Task(title=form.title.data,date=form.date.data,starttime=form.starttime.data, endtime=form.endtime.data,details=form.details.data,remindtime=form.remindtime.data,status=form.status.data,user_id=current_user.id,message_id=t)   
        db.session.add(task)
        db.session.commit()
        flash('Task added!','success')
        return redirect(url_for('task',task_id=task.id))
    elif request.method=='GET':
        form.details.data=subject #setting mail subject as taskdetails
    return render_template('create_task.html',form=form)


@application.route("/learn_more")
def learn_more():
    return render_template("howto-app_password.html")

@application.route("/contact_us",methods=['GET', 'POST'])
def contact_us():
    form=MessageForm()
    if current_user.is_authenticated:
        form.email.data=current_user.email
    if form.validate_on_submit():
        msg=Message('Sent by Durango user: '+current_user.username,sender=form.email.data,recipients=['durangoadmn@gmail.com']) 
        msg.body=f'''Sent from Durango contact us page:
        {form.message.data}

'''
        mail.send(msg)
        flash('Your message has been sent.','success')
    return render_template("contact_us.html",form=form)

@application.route("/see_user/<int:code>/<int:user_id>") #code is 0 for add connections and 1 for received connections
@login_required
def see_user(code,user_id):
    user=User.query.filter_by(id=user_id).first()
    return render_template("see_user.html",user=user,code=code)

@application.route("/add_connection/<int:user_b_id>", methods=["GET","POST"])
@login_required
def add_connection(user_b_id):
    """Send a connection request to another user."""

    user_a_id = current_user.id
    user_b=User.query.filter_by(id=user_b_id).first()
    # Check connection status between user_a and user_b
    is_connection, is_pending = is_connection_or_pending(user_a_id, user_b_id)
    status=is_pending
    if user_a_id == user_b_id:
        return "You cannot add yourself as a connection."
    elif is_connection:
        flash(user_b.username+' is already a connection.','info')
        return render_template("see_user.html",code=0,user=user_b)
    elif is_pending:
        flash('Your connection request is pending.','info')
        return render_template("see_user.html",code=0,user=user_b)
    else:
        requested_connection = Connection(user_a_id=user_a_id,
                                          user_b_id=user_b_id,
                                          status="Requested")
        db.session.add(requested_connection)
        db.session.commit()
        flash('Your connection request has been sent.','success')
        return render_template("see_user.html",code=0,user=user_b)

@application.route("/connections")
@login_required
def show_connections_and_requests():
    """Show connection requests and list of all connections"""

    # This returns User objects for current user's connection requests
    received_connection_requests, sent_connection_requests = get_connection_requests(current_user.id)

    # This returns User objects for current user's connection
    connections_1,connections_2 = get_connections(current_user.id)
    connections=connections_1.all()+connections_2.all()
    users=[]
    temps=User.query.all()
    for temp in temps:
        flag=0
        for c in connections:
            if temp.id==c.id:
                flag=1
                break
        if flag==0 and temp.id!=current_user.id:
            users.append(temp)
    return render_template("connections.html",
                           received_connection_requests=received_connection_requests,
                           sent_connection_requests=sent_connection_requests,
                           connections=connections,users=users)

@application.route("/accept_request/<int:user_a_id>")
@login_required
def accept_request(user_a_id):
    connection=Connection.query.filter_by(user_b_id=current_user.id, user_a_id=user_a_id).all()
    for c in connection:
        db.session.delete(c)
    # if current_user had send request to user_a it would also get accepted
    connection=Connection.query.filter_by(user_a_id=current_user.id,user_b_id=user_a_id).all()
    for c in connection:
        db.session.delete(c)
    c=Connection(user_a_id=user_a_id,user_b_id=current_user.id,status="Accepted")
    db.session.add(c)
    db.session.commit()
    sender=User.query.filter_by(id=user_a_id).first()
    flash(sender.username+' is now a connection!','success')
    return redirect(url_for('show_connections_and_requests'))

@application.route("/delete_request/<int:user_a_id>")
@login_required
def delete_request(user_a_id):
    connection=Connection.query.filter_by(user_b_id=current_user.id, user_a_id=user_a_id).all()
    for c in connection:
        c.status="Deleted"   
    db.session.commit()
    flash('Request deleted','info')
    return redirect(url_for('show_connections_and_requests'))

@application.route("/message_user/<int:receiver_id>",methods=['GET', 'POST'])
@login_required
def message_user(receiver_id):
    form=MessageForm()
    r=User.query.filter_by(id=receiver_id).first()
    if current_user.is_authenticated:
        form.email.data=current_user.email
    if form.validate_on_submit():
        msg=Message('Sent by Durango user: '+current_user.username,sender=form.email.data,recipients=[r.email]) 
        msg.body=f'''{current_user.username} says:
        {form.message.data}
'''
        mail.send(msg)
        flash('Your message has been sent.','success')
    return render_template("message_user.html",form=form)

@application.route("/chat/<int:user_id>")
@login_required
def chat(user_id):
    return render_template('session.html',user_id=user_id)

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

###chat socket
@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)
