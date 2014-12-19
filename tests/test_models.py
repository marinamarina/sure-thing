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
        self.match1 = Match.query.all()[len(matches)-2]
        self.match2 = Match.query.all()[len(matches)-1]

        self.u1.save_match(self.match1)
        self.u1.save_match(self.match2)
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

        #testing the saved matches array length
        self.assertTrue(self.u1.list_matches(), 'User saved matches for later revision' )

        print ('\n--------TESTING DEFAULT SYSTEM CONFIGURATION-------')
        print ('\n--------TESTING MATCH 1-------')

        match1 = self.u1.list_matches()[0].match
        #testing default configuration
        print match1.hometeam, match1.awayteam
        print ('--------testing league position prediction module-------')

        #user with lower league position is a winner of module 'league position'
        if int(match1.hometeam.position) > int(match1.awayteam.position):
            self.assertTrue(match1.prediction_league_position == match1.awayteam)
        else:
            self.assertTrue(match1.prediction_league_position == match1.hometeam)

        print 'LEAGUE_POSITION WINNER: {}, %: {}'.format(str(match1.prediction_league_position),
                                                         PredictionModule.query.filter_by(id=1).first().default_weight
                                              )
        print  'FORM WINNER: {}, %: {}'.format(str(match1.prediction_form),
                                               PredictionModule.query.filter_by(id=2).first().default_weight
                                               )
        print  'HOME_AWAY WINNER: {}, %:{}'.format(str(match1.prediction_homeaway),
                                                   PredictionModule.query.filter_by(id=3).first().default_weight
                                               )

        print 'OVERALL WINNER: {}'.format( str(Match.predicted_winner(match1)) )

        print ('\n--------TESTING MATCH 2-------')
        match2 = self.u1.list_matches()[1].match
        #testing default configuration
        print match2.hometeam, match2.awayteam
        print ('--------testing league position prediction module-------')

        #user with lower league position is a winner of module 'league position'
        if int(match2.hometeam.position) > int(match2.awayteam.position):
            self.assertTrue(match2.prediction_league_position == match2.awayteam)
        else:
            self.assertTrue(match2.prediction_league_position == match2.hometeam)

        print 'LEAGUE_POSITION WINNER: {}, %: {}'.format(str(match2.prediction_league_position),
                                                         PredictionModule.query.filter_by(id=1).first().default_weight
                                              )
        print  'FORM WINNER: {}, %: {}'.format(str(match2.prediction_form),
                                               PredictionModule.query.filter_by(id=2).first().default_weight
                                               )
        print  'HOME_AWAY WINNER: {}, %:{}'.format(str(match2.prediction_homeaway),
                                                   PredictionModule.query.filter_by(id=3).first().default_weight
                                               )

        print 'OVERALL WINNER: {}'.format( str(Match.predicted_winner(match2)) )

