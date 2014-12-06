#!/usr/bin/env python
import os
from flask_script import Manager, Shell
from app import create_app, db
from app.models import User, Role, Permission, Follow, Team, Match, SavedForLater, PredictionModule
from flask_migrate import Migrate, MigrateCommand
from app import socketio

basedir = os.path.abspath(os.path.dirname(__file__))

cov = None
if (os.environ.get('FLASK_COVERAGE')):
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
                Follow=Follow,
                Team=Team, Match=Match,
                SavedForLater=SavedForLater,
                PredictionModule=PredictionModule)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

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


if __name__ == '__main__':
    socketio.run(app)
    manager.run()