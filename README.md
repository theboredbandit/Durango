Flask App-Durango

#If python3 is not installed, install via:

$ sudo apt-get update

$ sudo apt-get install python3.6.9



#Install pip and virtualenv:
$ sudo apt install python3-pip

$ sudo pip3 install virtualenv


Create a virtual environment

$ virtualenv project_env

$ source project_env/bin/activate

(project_env) skg@skg:~$ cd Durango



Installation

Use the package manager pip to install dependencies.

(project_env) skg@skg:~/Durango$ pip install -r requirements.txt



Run app

# Start the server in terminal:

(project_env) skg@skg:~/Durango$ python application.py

#In other terminal window start celery worker:

(project_env) skg@skg:~/Durango$ celery -A durango.celery worker --loglevel=INFO

# Open your browser and enter http://localhost:5000/ as the url.







