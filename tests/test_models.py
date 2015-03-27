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
        #create user roles
        Role.insert_roles()
        #insert matches from the data file
        Team.insert_teams()
        #insert modules
        PredictionModule.insert_modules()
        #insert matches from the data file
        Match.update_all_matches()
        self.u1 = User(email='jenny@example.com', password='cat')
        self.u1.confirmed = True
        db.session.add(self.u1)
        db.session.commit()
        matches = Match.query.all()

        #non-played
        self.match1 = Match.query.all()[len(matches) - 2]
        self.match2 = Match.query.all()[len(matches) - 1]


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

    @unittest.skip("")
    def test_saved_matches_length(self):
        self.assertTrue(self.u1.list_matches(), 'User saved matches for later revision' )
        self.assertTrue(len(self.u1.list_matches()) == 5, 'User saved exactly 5 matches' )

    @unittest.skip("")
    def test_default_prediction(self):

        print ('\n--------TESTING DEFAULT SYSTEM CONFIGURATION-------')
        print ('\n--------TESTING MATCH 1-------')

        match1 = self.u1.list_matches()[0].match
        #testing default configuration
        print match1.hometeam, match1.awayteam
        print ('--------testing league position prediction module-------')

        if self.prediction_league_position(match1) > 0:
            self.assertTrue(match1.prediction_league_position > 0)
        else:
            self.assertTrue(match1.prediction_league_position < 0)

        print 'LEAGUE_POSITION VALUE: {}% * {}%'.format(str(match1.prediction_league_position),
                                                        int(PredictionModule.query.filter_by(id=1).first().weight) * 100
                                                        )

        if self.prediction_form(match1) > 0:
            self.assertTrue(match1.prediction_form > 0)
        else:
            self.assertTrue(match1.prediction_form < 0)

        print 'FORM VALUE: {}% * {}%'.format(str(match1.prediction_form),
                                               int(PredictionModule.query.filter_by(id=2).first().weight) * 100
                                               )

        if self.prediction_homeaway(match1) > 0:
            self.assertTrue(match1.prediction_homeaway > 0)
        else:
            self.assertTrue(match1.prediction_homeaway < 0)

        print 'HOME_AWAY VALUE: {}% * {}%'.format(str(match1.prediction_homeaway),
                                                  int(PredictionModule.query.filter_by(id=3).first().weight) * 100
                                                  )

        print ('\n--------TESTING MATCH 2-------')

        match2 = self.u1.list_matches()[1].match
        #testing default configuration
        print match2.hometeam, match2.awayteam
        print ('--------testing league position prediction module-------')

        if self.prediction_league_position(match2) > 0:
            self.assertTrue(match2.prediction_league_position > 0)
        else:
            self.assertTrue(match2.prediction_league_position < 0)

        print 'LEAGUE_POSITION VALUE: {}% * {}%'.format(str(match2.prediction_league_position),
                                                        int(PredictionModule.query.filter_by(id=1).first().weight) * 100
                                                        )

        if self.prediction_form(match2) > 0:
            self.assertTrue(match2.prediction_form > 0)
        else:
            self.assertTrue(match2.prediction_form < 0)

        print 'FORM VALUE: {}% * {}%'.format(str(match2.prediction_form),
                                            int(PredictionModule.query.filter_by(id=2).first().weight) * 100
                                            )

        if self.prediction_homeaway(match2) > 0:
            self.assertTrue(match2.prediction_homeaway > 0)
        else:
            self.assertTrue(match2.prediction_homeaway < 0)

        print 'HOME_AWAY VALUE: {}% * {}%'.format(str(match2.prediction_homeaway),
                                                  int(PredictionModule.query.filter_by(id=3).first().weight) * 100
                                                  )

        """
        print 'OVERALL WINNER: {}'.format( str(Match.predicted_winner(match1)) )

        """

    def prediction_league_position(self, match):
        hometeam_diff = 20 - int(match.hometeam.position)
        awayteam_diff = 20 - int(match.awayteam.position)
        prediction_value = (hometeam_diff - awayteam_diff) * 100 / 19

        return prediction_value

    def prediction_form(self, match):
        hometeam_pts = match.hometeam.form_last_6.pts
        awayteam_pts = match.awayteam.form_last_6.pts
        prediction_value = (hometeam_pts - awayteam_pts) * 100 / 18

        return prediction_value

    def prediction_homeaway(self, match):
        hometeam_home_pts = match.hometeam.form_home_away.home.pts

        # awayteam's performance away (last 6 matches)
        awayteam_away_pts = match.awayteam.form_home_away.away.pts

        prediction_value = (hometeam_home_pts - awayteam_away_pts) * 100 / 18

        return prediction_value

    @unittest.skip("")
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


    @unittest.skip("")
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


    @unittest.skip("")
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

    @unittest.skip("")
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


    @unittest.skip("")
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


    @unittest.skip("TO DO: TEST user hunch contrib to DRAW, contrib to changing result")
    def test_user_hunch_module(self):
        pass


    @unittest.skip('')
    def test_winning_config(self):
        match=Match.query.filter_by(id=1963810).first()
        pass


