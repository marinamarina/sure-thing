import unittest
from flask import current_app
from app import create_app, db
from pprint import pprint
from app.football_data.football_api_wrapper import FootballAPIWrapper
from app.models import PredictionModule, Role, Match, User, Team, SavedForLater, ModuleUserSettings

class TestPredictionSettings(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        Team.insert_teams()
        PredictionModule.insert_modules()
        Match.update_all_matches()
        self.u1 = User(email='john@example.com', password='cat')
        self.u1.confirmed = True
        db.session.add(self.u1)
        db.session.commit()
        matches = Match.query.all()
        self.match = Match.query.all()[len(matches)-2]
        self.u1.save_match( self.match )
        db.session.add(self.u1)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_league_position(self):
        #print(self.match.hometeam)
        pass


    def test_default_prediction(self):

        self.assertTrue(len(self.u1.list_matches()) > 0, 'User saved a match' )
        match = self.u1.list_matches()[0].match
         #default configuration
        modules_winners = [match.prediction_league_position, match.prediction_form, match.prediction_homeaway]
        #print match.hometeam, match.awayteam
        #print match.prediction_league_position
        #print match.prediction_form
        #print match.prediction_homeaway

        print Match.predicted_winner(match, modules_winners)

    def test_user_prediction(self):

        self.assertTrue(len(self.u1.list_matches()) > 0, 'User saved a match' )
        match = self.u1.list_matches()[0].match
         #default configuration
        modules_winners = [match.prediction_league_position, match.prediction_form, match.prediction_homeaway]

        m1 = ModuleUserSettings(user_id=self.u1.id, module_id=1, weight=0.12)
        m2 = ModuleUserSettings(user_id=self.u1.id, module_id=2, weight=0.32)
        m3 = ModuleUserSettings(user_id=self.u1.id, module_id=3, weight=0.56)
        db.session.add(m1)
        db.session.add(m2)
        db.session.add(m3)
        db.session.commit()

        print ModuleUserSettings.query.filter_by(user_id=self.u1.id).all()

        print match.hometeam, match.awayteam
        print match.prediction_league_position
        print match.prediction_form
        print match.prediction_homeaway

        print Match.predicted_winner(match, modules_winners, self.u1)