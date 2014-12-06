from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_shorturl import ShortUrl
from config import config
from gevent import monkey
from threading import Thread, Event
from flask_socketio import SocketIO
import atexit
from football_data.football_api_wrapper import FootballAPIWrapper

#gunicorn -b 0.0.0.0:5000 --log-config log.conf --pid=app.pid myfile:app

monkey.patch_all()

bootstrap = Bootstrap()
mail = Mail()
#database representation
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
su = ShortUrl()
faw = FootballAPIWrapper()
faw.api_key = '2890be06-81bd-b6d7-1dcb4b5983a0' # set as an environment variable
socketio = SocketIO()


'''POOL_TIME = 120 #600 #seconds equals 10 minutes

# variables that are accessible from anywhere
commonDataStruct = {}

# lock to control access to variable
dataLock = threading.Lock()

# thread handler
mathesDataThread = threading.Thread()'''

'''def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        time.sleep(10)
        count += 1
        threads.emit('my response',
                      {'data': 'Data updated', 'count': count},
                      namespace='/test')'''


def create_app(config_name):
    app = Flask(__name__)

    #loading configurations into the app
    app.config.from_object(config[config_name])

    #initialise the application
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    with app.app_context():
        # Extensions like Flask-SQLAlchemy now know what the "current" app
        # is while within this block. Therefore, you can now run........
        db.create_all()

    faw.init_app(app)
    login_manager.init_app(app)
    su.init_app(app)
    socketio.init_app(app)

    #attach routes and custom error pages here
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app

''' # take care of a multithreading
    def interrupt():
        global matchesDataThread
        dataThread.cancel()

    def loadData():
        global commonDataStruct
        global dataThread
        global dataLock
        with dataLock:
            print('Data reloaded at ' + datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
            #faw.write_data()

        # Set the next thread to happen
        dataThread = threading.Timer(POOL_TIME, loadData, ())
        dataThread.start()

    def loadDataStart():
        # Do initialisation stuff here
        global dataThread
        # Create your thread
        dataThread = threading.Timer(POOL_TIME, loadData, ())
        dataThread.start()

    # Initiate
    loadDataStart()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)'''