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

        #non-played
        self.match1 = Match.query.all()[len(matches)-2]
        self.match2 = Match.query.all()[len(matches)-1]


        #played
        self.match3 = Match.query.all()[12]
        self.match4 = Match.query.all()[16]

        #draw
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

    @unittest.skip('')
    def test_league_position(self):
        #print(self.match.hometeam)
        pass


    @unittest.skip('')
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

        print 'OVERALL WINNER: {}'.format( str(Match.predicted_winner(match2, self.u1)) )

    @unittest.skip('')
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

    @unittest.skip('')
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

    @unittest.skip('')
    def test_multiple_users_match_predictions(self):
        # this is tested match
        match1 = self.u1.list_matches()[0].match
        # add another user
        u2 = User(email='scarlett@example.com', password='cat')
        u2.confirmed = True
        db.session.add(u2)
        db.session.commit()
        print ('\n--------TESTING MULTIPLE USERS CONFIGURATION-------')
        print ('--------TESTCASE-1 USERS HAS ONLY MATCH SETTINGS-------')

        # specific match settings for user 1
        mus1_1=ModuleUserMatchSettings(user_id=self.u1.id, match_id=self.match1.id, module_id=1, weight=0.09)
        mus2_1=ModuleUserMatchSettings(user_id=self.u1.id, match_id=self.match1.id, module_id=2, weight=0.40)
        mus3_1=ModuleUserMatchSettings(user_id=self.u1.id, match_id=self.match1.id, module_id=3, weight=0.51)

         # specific match settings for user 2
        mus1_2=ModuleUserMatchSettings(user_id=u2.id, match_id=self.match1.id, module_id=1, weight=0.08)
        mus2_2=ModuleUserMatchSettings(user_id=u2.id, match_id=self.match1.id, module_id=2, weight=0.40)
        mus3_2=ModuleUserMatchSettings(user_id=u2.id, match_id=self.match1.id, module_id=3, weight=0.52)

        db.session.add(mus1_1)
        db.session.add(mus2_1)
        db.session.add(mus3_1)
        db.session.add(mus1_2)
        db.session.add(mus2_2)
        db.session.add(mus3_2)
        db.session.commit()

        print match1.hometeam, match1.awayteam
        print 'LEAGUE_POSITION WINNER: {}, %: {}'.format(str(match1.prediction_league_position),
                                                         mus1_2.weight
                                              )
        print 'FORM WINNER: {}, %: {}'.format(str(match1.prediction_form),
                                               mus2_2.weight
                                               )
        print 'HOME_AWAY WINNER: {}, %:{}'.format(str(match1.prediction_homeaway),
                                                mus3_2.weight
                                               )

        print 'OVERALL WINNER: {}'.format( str(Match.predicted_winner(match1, u2)) )

        # check the probability is correct (picked up from the settings of the second user)
        if(match1.prediction_homeaway.id==9127):
            self.assertEqual(Match.predicted_winner(match1, u2).probability, 0.52)
        else:
            self.assertGreaterEqual(Match.predicted_winner(match1, u2).probability, 0.48)


    def test_lsp(self):
        print ('\n-----------------TESTING LSP---------------------')
        match1 = self.u1.list_matches()[0]
        #print 'THIS IS THE VALUE' + str (match1.)
        #self.assertTrue(match1.update_lsp('3/1') == 4, 'LSP is equal to a certain value')


    def test_actual_winner(self):
        print ('\n\n-----------------ACTUAL WINNER---------------------')

        # test a match
        match3 = self.u1.list_matches()[0]
        print match3
        print 'WAS PLAYED?' + str(match3.match.date)
        print 'Score is '+ str(match3.match.hometeam_score) + ':' +str(match3.match.awayteam_score)

        print 'Actual winner: ' + str(match3.match.actual_winner)
        self.assertEqual(match3.match.actual_winner, 9092, 'Actual winner was Chelsea')

        # test draw
        match4 = self.u1.list_matches()[1]
        print match4
        print 'WAS PLAYED?' + str(match4.match.date)
        print 'Score is '+ str(match4.match.hometeam_score) + ':' +str(match4.match.awayteam_score)

        print 'Actual winner: ' + str(match4.match.actual_winner)
        self.assertEqual(match4.match.actual_winner, -1, 'This is draw')

        # test another match
        match5 = self.u1.list_matches()[2]
        print match5
        print 'WAS PLAYED?' + str(match5.match.date)
        print 'Score is '+ str(match5.match.hometeam_score) + ':' +str(match5.match.awayteam_score)

        print 'Actual winner: ' + str(match5.match.actual_winner)
        self.assertEqual(match5.match.actual_winner, 9259, 'Actual winner was Man City')


    def test_bettor_won(self):
        print ('\n\n-----------------BETTOR WON---------------------')
        match3 = self.u1.list_matches()[0]
        match4 = self.u1.list_matches()[1]
        match3.committed=True
        match4.committed=True

        db.session.add(match3)
        db.session.add(match4)
        db.session.commit()
        print 'Predicted winner is ' + str (Match.predicted_winner(user=self.u1,match=match3.match).team_winner_id)
        print 'Actual winner is ' + str(match3.match.actual_winner)
        print 'Predicted winner is ' + str (Match.predicted_winner(user=self.u1,match=match4.match).team_winner_id)
        print 'Actual winner is ' + str(match4.match.actual_winner)

        # user guessed it correctly
        self.assertTrue(match3.bettor_won, 'User predicted match result correctly')

        # the actual result is a draw, user predicted home win
        self.assertFalse(match4.bettor_won, 'User predicted match result correctly')

        # change the settings so user predicts draw
        mus1=ModuleUserMatchSettings(user_id=self.u1.id, match_id=match4.match.id, module_id=1, weight=0.2)
        mus2=ModuleUserMatchSettings(user_id=self.u1.id, match_id=match4.match.id, module_id=2, weight=0.3)
        mus3=ModuleUserMatchSettings(user_id=self.u1.id, match_id=match4.match.id, module_id=3, weight=0.5)

        db.session.add(mus1)
        db.session.add(mus2)
        db.session.add(mus3)
        db.session.commit()

        user_match_prediction_settings = self.u1.list_match_specific_settings(match_id=match4.match.id)

        print user_match_prediction_settings


        print match4.match.hometeam, match4.match.awayteam
        print 'LEAGUE_POSITION WINNER: {}, %: {}'.format(str(match4.match.prediction_league_position),
                                                         mus1.weight
                                              )
        print  'FORM WINNER: {}, %: {}'.format(str(match4.match.prediction_form),
                                               mus2.weight
                                               )
        print  'HOME_AWAY WINNER: {}, %:{}'.format(str(match4.match.prediction_homeaway),
                                                mus3.weight
                                               )

        print 'OVERALL WINNER: {}'.format( str(Match.predicted_winner(match4.match, self.u1)) )

        self.assertTrue(match4.bettor_won, 'User predicted match result correctly')

