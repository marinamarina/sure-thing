from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_shorturl import ShortUrl
from config import config
import threading
import atexit

from football_data.football_api_parser import FootballAPIWrapper

#gunicorn -b 0.0.0.0:5000 --log-config log.conf --pid=app.pid myfile:app


bootstrap = Bootstrap()
mail = Mail()
#database representation
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
su = ShortUrl()
faw = FootballAPIWrapper()
faw.api_key = '2890be06-81bd-b6d7-1dcb4b5983a0'

POOL_TIME = 600 #seconds equals 10 minutes

# variables that are accessible from anywhere
commonDataStruct = {}

# lock to control access to variable
dataLock = threading.Lock()

# thread handler
yourThread = threading.Thread()


def create_app(config_name):
    app = Flask(__name__)

    #loading configurations into the app
    app.config.from_object(config[config_name])

    #initialise the application
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    faw.init_app(app)
    login_manager.init_app(app)
    su.init_app(app)

    # take care of a multithreading
    def interrupt():
        global yourThread
        yourThread.cancel()

    def doStuff():
        global commonDataStruct
        global yourThread
        global dataLock
        with dataLock:
            print('data reloaded')
            faw.write_data()

        # Set the next thread to happen
        yourThread = threading.Timer(POOL_TIME, doStuff, ())
        yourThread.start()

    def doStuffStart():
        # Do initialisation stuff here
        global yourThread
        # Create your thread
        yourThread = threading.Timer(POOL_TIME, doStuff, ())
        yourThread.start()

    # Initiate
    doStuffStart()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)


    #attach routes and custom error pages here
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app