import unittest
from app import create_app, db
from pprint import pprint
from app.models import PredictionModule, Role, Match, User, Team, ModuleUserMatchSettings, ModuleUserSettings

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

        print 'OVERALL WINNER: {}'.format( str(Match.predicted_winner(match1, self.u1)) )

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

        print 'OVERALL WINNER: {}'.format( str(Match.predicted_winner(match2, self.u1)) )

    def test_user_prediction(self):
        print ('\n--------TESTING DEFAULT USER CONFIGURATION-------')

        self.assertTrue(self.u1.list_matches(), 'User saved matches to the dashboard' )
        match1 = self.u1.list_matches()[0].match

        #default configuration
        us1 = ModuleUserSettings(user_id=self.u1.id, module_id=1, weight=0.12)
        us2 = ModuleUserSettings(user_id=self.u1.id, module_id=2, weight=0.32)
        us3 = ModuleUserSettings(user_id=self.u1.id, module_id=3, weight=0.56)
        db.session.add(us1)
        db.session.add(us2)
        db.session.add(us3)
        db.session.commit()

        print ModuleUserSettings.query.filter_by(user_id=self.u1.id).all()

        print match1.hometeam, match1.awayteam
        print 'LEAGUE_POSITION WINNER: {}, %: {}'.format(str(match1.prediction_league_position),
                                                         us1.weight
                                              )
        print  'FORM WINNER: {}, %: {}'.format(str(match1.prediction_form),
                                               us2.weight
                                               )
        print  'HOME_AWAY WINNER: {}, %:{}'.format(str(match1.prediction_homeaway),
                                                   us3.weight
                                               )

        print 'OVERALL WINNER: {}'.format( str(Match.predicted_winner(match1, self.u1)) )

    def test_user_match_prediction(self):
        print ('\n--------TESTING MATCH SPECIFIC USER CONFIGURATION-------')
        print ('--------TESTCASE-1 USER HAS ONLY MATCH SETTINGS-------')

        mus1=ModuleUserMatchSettings(user_id=self.u1.id, match_id=self.match1.id, module_id=1, weight=0.11)
        mus2=ModuleUserMatchSettings(user_id=self.u1.id, match_id=self.match1.id, module_id=2, weight=0.38)
        mus3=ModuleUserMatchSettings(user_id=self.u1.id, match_id=self.match1.id, module_id=3, weight=0.51)

        db.session.add(mus1)
        db.session.add(mus2)
        db.session.add(mus3)
        db.session.commit()

        user_match_prediction_settings = self.u1.list_match_specific_settings(match_id=self.match1.id)

        print user_match_prediction_settings
        match1 = self.u1.list_matches()[0].match


        print match1.hometeam, match1.awayteam
        print 'LEAGUE_POSITION WINNER: {}, %: {}'.format(str(match1.prediction_league_position),
                                                         mus1.weight
                                              )
        print  'FORM WINNER: {}, %: {}'.format(str(match1.prediction_form),
                                               mus2.weight
                                               )
        print  'HOME_AWAY WINNER: {}, %:{}'.format(str(match1.prediction_homeaway),
                                                mus3.weight
                                               )

        print 'OVERALL WINNER: {}'.format( str(Match.predicted_winner(match1, self.u1)) )

        print ('\n--------TESTCASE-2 USER HAS USER DEFAULT AND MATCH SPECIFIC SETTINGS-------')
        #default configuration
        us1 = ModuleUserSettings(user_id=self.u1.id, module_id=1, weight=0.12)
        us2 = ModuleUserSettings(user_id=self.u1.id, module_id=2, weight=0.32)
        us3 = ModuleUserSettings(user_id=self.u1.id, module_id=3, weight=0.56)
        db.session.add(us1)
        db.session.add(us2)
        db.session.add(us3)
        db.session.commit()

        print match1.hometeam, match1.awayteam
        print 'LEAGUE_POSITION WINNER: {}, %: {}'.format(str(match1.prediction_league_position),
                                                         mus1.weight
                                              )
        print  'FORM WINNER: {}, %: {}'.format(str(match1.prediction_form),
                                               mus2.weight
                                               )
        print  'HOME_AWAY WINNER: {}, %:{}'.format(str(match1.prediction_homeaway),
                                                mus3.weight
                                               )

        print 'OVERALL WINNER: {}'.format( str(Match.predicted_winner(match1, self.u1)) )