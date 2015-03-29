import unittest
from app import create_app, db
from app.models import PredictionModule, Role, Match, User, Team, Message


class TestNotifications(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        #create user roles
        Role.insert_roles()
        #insert matches from the data file
        Team.insert_teams()
        #insert modules
        PredictionModule.insert_modules()
        #insert matches from the data file
        Match.update_all_matches()
        self.u1 = User(email='alison@example.com', password='cat')
        self.u1.confirmed = True
        db.session.add(self.u1)
        db.session.commit()
        matches = Match.query.all()

        # couple of non-played matches
        self.match1 = Match.query.all()[len(matches) - 2]
        self.match2 = Match.query.all()[len(matches) - 1]

        # some played matches
        self.match3 = Match.query.all()[12]
        self.match4 = Match.query.all()[16]

        # draw match
        self.match5 = Match.query.all()[14]

        self.u1.save_match(self.match1)
        self.u1.save_match(self.match2)
        self.u1.save_match(self.match3)
        self.u1.save_match(self.match4)
        self.u1.save_match(self.match5)
        db.session.add(self.u1)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def addMessage(self):
        print