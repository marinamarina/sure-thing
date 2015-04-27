from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_moment import Moment
from config import config
from gevent import monkey
from flask_socketio import SocketIO
from football_data.football_api_wrapper import FootballAPIWrapper
from celery import Celery
import redis


#gunicorn -b 0.0.0.0:5000 --log-config log.conf --pid=app.pid myfile:app

monkey.patch_all()

bootstrap = Bootstrap()
mail = Mail()
#database representation
db = SQLAlchemy(session_options={'expire_on_commit': False})

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
moment = Moment()
faw = FootballAPIWrapper()
faw.api_key = '2890be06-81bd-b6d7-1dcb4b5983a0' # set as an environment variable
socketio = SocketIO()


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

    # Celery configuration
    app.config.update(
        CELERY_BROKER_URL='redis://localhost:6379'
    )

    #initialise the application
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    db.init_app(app)

    with app.app_context():
        # Extensions like Flask-SQLAlchemy now know what the "current" app
        # is while within this block. Therefore, you can now run........
        db.create_all()

    moment.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)

    #attach routes and custom error pages here
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app