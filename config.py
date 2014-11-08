import os

# absolute path to this script
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # encryption key, storing in an environment variable
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(23)
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT=465
    MAIL_USE_TLS=False
    MAIL_USE_SSL=True
    MAIL_USERNAME = 'shchukina.marina@gmail.com '#os.environ.get('FOOTY_ADMIN')
    MAIL_PASSWORD = 'sezblpfzltnulpbr'#os.environ.get('MAIL_PASSWORD')
    FOOTY_MAIL_SUBJECT_PREFIX = 'SURETHING ADMIN '
    FOOTY_MAIL_SENDER='Sure thing <surething@admin.com>'
    FOOTY_ADMIN = """os.environ.get('SURETHING_ADMIN') or""" 'shchukina.marina@gmail.com'
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class DeploymentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

@classmethod
def init_app(cls, app):
    DevelopmentConfig.Config.init_app(app)

    #log to stderr
    import logging
    from logging import StreamHandler
    file_handler = StreamHandler()
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

# config dictionary
# mapping various configurations
config = {
    'development' : DevelopmentConfig,
    'testing' : TestingConfig,
    'deployment' : DeploymentConfig,

    'default' : DevelopmentConfig
}
