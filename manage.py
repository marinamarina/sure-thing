import os
from app import create_app, db
from app.models import User, Role, Permission, Follow, \
    Team, Match, SavedForLater, \
    PredictionModule, \
    ModuleUserSettings, \
    ModuleUserMatchSettings, \
    Message
from flask_migrate import Migrate, MigrateCommand, upgrade
from flask_script.commands import Server, Shell, ShowUrls, Clean
from app import socketio


from flask.ext.script import Manager

basedir = os.path.abspath(os.path.dirname(__file__))
port = 5000

cov = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    cov = coverage.coverage(branch=True, include='app/*')
    cov.start()

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    """make app, db available to the command line"""
    return dict(app=app, db=db, User=User, Role=Role,
                Permission=Permission,
                Follow=Follow, Message=Message,
                Team=Team, Match=Match,
                SavedForLater=SavedForLater,
                PredictionModule=PredictionModule,
                ModuleUserSettings=ModuleUserSettings,
                ModuleUserMatchSettings=ModuleUserMatchSettings)

manager.add_command("shell", Shell(make_context=make_shell_context, use_bpython=True))
manager.add_command("db", MigrateCommand)
manager.add_command("show_urls", ShowUrls())
manager.add_command("clean", Clean())

@manager.command
def runserver(debug=True): #needs to be changed to False in production or for updating the data
    app.debug = debug
    socketio.run(app, host='127.0.0.1', port=port)

@manager.command
def test(coverage=False):

    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    import unittest

    tests = unittest.TestLoader().discover('tests')
    #Run the unittests

    unittest.TextTestRunner(verbosity=2).run(
        tests
    )

    if cov:
        cov.stop()
        cov.save()
        print ("\n\nCoverage Report:\n")
        cov.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        cov.html_report(directory = covdir)
        print('HTML version: file://%s/index.html' % covdir)
        cov.erase()
@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run()

@manager.command
def deploy():
    """Deployment tasks"""
    #migrate database to latest revision
    upgrade()
    #create user roles
    Role.insert_roles()
    #insert matches from the data file
    Team.insert_teams()
    #insert matches from the data file
    Match.update_all_matches()
    #insert modules
    PredictionModule.insert_modules()

if __name__ == '__main__':
    manager.run()