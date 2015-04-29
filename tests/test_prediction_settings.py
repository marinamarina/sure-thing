import unittest
from app import create_app, db
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

    def test_saved_matches_were_saved(self):
        self.assertTrue(self.u1.list_matches(), 'Match list associated with the user is not empty')
        self.assertTrue(len(self.u1.list_matches()) == 5, 'User saved exactly 5 matches')

    def test_system_default_prediction_settings(self):
        # TESTING DEFAULT SYSTEM CONFIGURATION
        # TESTING MATCH1
        match1 = self.u1.list_matches()[0].match

        #testing default configuration
        #testing league position prediction module
        if self.prediction_league_position(match1) > 0:
            self.assertTrue(match1.prediction_league_position > 0)
        else:
            self.assertTrue(match1.prediction_league_position <= 0)

        if self.prediction_form(match1) > 0:
            self.assertTrue(match1.prediction_form > 0)
        else:
            self.assertTrue(match1.prediction_form <= 0)

        # testing form prediction module
        if self.prediction_form(match1) > 0:
            self.assertTrue(match1.prediction_form > 0)
        else:
            self.assertTrue(match1.prediction_form <= 0)

        # testing home/away prediction module
        if self.prediction_homeaway(match1) > 0:
            self.assertTrue(match1.prediction_homeaway > 0)
        else:
            self.assertTrue(match1.prediction_homeaway <= 0)

        # TESTING MATCH 2
        match2 = self.u1.list_matches()[1].match

        #testing default configuration

        # testing league position prediction module
        if self.prediction_league_position(match2) > 0:
            self.assertTrue(match2.prediction_league_position > 0)
        else:
            self.assertTrue(match2.prediction_league_position <= 0)

        if self.prediction_form(match2) > 0:
            self.assertTrue(match2.prediction_form > 0)
        else:

            self.assertTrue(match2.prediction_form <= 0)

        # testing form prediction module
        if self.prediction_homeaway(match2) > 0:
            self.assertTrue(match2.prediction_homeaway > 0)
        else:
            self.assertTrue(match2.prediction_homeaway <= 0)

        # testing home/away prediction module
        if self.prediction_homeaway(match2) > 0:
            self.assertTrue(match2.prediction_homeaway > 0)
        else:
            self.assertTrue(match2.prediction_homeaway <= 0)

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

    def test_user_default_prediction_settings(self):
        # TESTING USER  DEFAULT CONFIGURATION
        self.assertTrue(self.u1.list_matches(), 'User saved matches to the dashboard')
        match1 = self.u1.list_matches()[0].match

        user_default_settings = [0.12, 0.32, 0.56]

        # user default settings
        us1 = ModuleUserSettings(user_id=self.u1.id, module_id=1, weight=user_default_settings[0])
        us2 = ModuleUserSettings(user_id=self.u1.id, module_id=2, weight=user_default_settings[1])
        us3 = ModuleUserSettings(user_id=self.u1.id, module_id=3, weight=user_default_settings[2])
        db.session.add(us1)
        db.session.add(us2)
        db.session.add(us3)
        db.session.commit()

        for i in range(0, len(user_default_settings)):
            self.assertEqual(ModuleUserSettings.query.filter_by(user_id=self.u1.id).all()[i].weight,
                             user_default_settings[i], "Check that the user default values are in database")

        # Check that for the calculation are used user default settings
        probability = match1.prediction_league_position * us1.weight \
            + match1.prediction_form * us2.weight \
            + match1.prediction_homeaway * us3.weight

        self.assertAlmostEqual(probability, Match.predicted_winner(match1, self.u1).probability)

    def test_match_specific_prediction_settings(self):

        # TESTING MATCH SPECIFIC USER CONFIGURATION
        # TESTCASE-1 USER HAS ONLY MATCH SETTINGS
        match_specific_settings = [0.11, 0.38, 0.51]
        match1 = self.u1.list_matches()[0].match
        u1 = self.u1

        mss1 = ModuleUserMatchSettings(user_id=self.u1.id, match_id=match1.id, module_id=1,
                                       weight=match_specific_settings[0])
        mss2 = ModuleUserMatchSettings(user_id=self.u1.id, match_id=match1.id, module_id=2,
                                       weight=match_specific_settings[1])
        mss3 = ModuleUserMatchSettings(user_id=self.u1.id, match_id=match1.id, module_id=3,
                                       weight=match_specific_settings[2])

        db.session.add(mss1)
        db.session.add(mss2)
        db.session.add(mss3)
        db.session.commit()

        self.assertEqual(len(u1.list_match_specific_settings(match_id=match1.id)), 3,
                         "Length of the list containing match specific settings is equal to 3")

        for i in range(0, len(match_specific_settings)):
            self.assertEqual(ModuleUserMatchSettings.query.filter_by(user_id=self.u1.id).all()[i].weight,
                             match_specific_settings[i], "Check that the match specific values are in database")

        # Check that for the calculation are used match specific settings
        probability = match1.prediction_league_position * mss1.weight \
            + match1.prediction_form * mss2.weight \
            + match1.prediction_homeaway * mss3.weight

        self.assertAlmostEqual(probability, Match.predicted_winner(match1, u1).probability)

        # TESTCASE-2 USER HAS BOTH USER DEFAULT AND MATCH SPECIFIC SETTINGS
        # default configuration
        user_default_settings = [0.12, 0.32, 0.56]
        us1 = ModuleUserSettings(user_id=self.u1.id, module_id=1, weight=user_default_settings[0])
        us2 = ModuleUserSettings(user_id=self.u1.id, module_id=2, weight=user_default_settings[1])
        us3 = ModuleUserSettings(user_id=self.u1.id, module_id=3, weight=user_default_settings[2])
        db.session.add(us1)
        db.session.add(us2)
        db.session.add(us3)
        db.session.commit()

        for i in range(0, len(user_default_settings)):
            self.assertEqual(ModuleUserSettings.query.filter_by(user_id=self.u1.id).all()[i].weight,
                             user_default_settings[i], "Check that the user default weights are in database")

        self.assertEqual(len(u1.list_prediction_settings()), 3, "List user default prediction settings is not empty")

        # Check that for the calculation are still used match specific settings, as they have priority
        self.assertAlmostEqual(probability, Match.predicted_winner(match1, u1).probability)

    def test_multiple_users_match_predictions(self):
        # this is tested match
        match1 = self.u1.list_matches()[0].match
        u1 = self.u1
        # add another user
        u2 = User(email='scarlett@example.com', password='cat')
        u2.confirmed = True
        db.session.add(u2)
        db.session.commit()

        # TESTING MULTIPLE USERS CONFIGURATION
        # TESTCASE-1 USERS HAVE ONLY MATCH SETTINGS
        user1_match_specific_settings = [0.09, 0.40, 0.51]
        user2_match_specific_settings = [0.08, 0.40, 0.52]

        # specific match settings for user 1
        mss1_1 = ModuleUserMatchSettings(user_id=self.u1.id, match_id=match1.id, module_id=1,
                                         weight=user1_match_specific_settings[0])
        mss2_1 = ModuleUserMatchSettings(user_id=self.u1.id, match_id=match1.id, module_id=2,
                                         weight=user1_match_specific_settings[1])
        mss3_1 = ModuleUserMatchSettings(user_id=self.u1.id, match_id=match1.id, module_id=3,
                                         weight=user1_match_specific_settings[2])

        # specific match settings for user 2
        mss1_2 = ModuleUserMatchSettings(user_id=u2.id, match_id=match1.id, module_id=1,
                                         weight=user2_match_specific_settings[0])
        mss2_2 = ModuleUserMatchSettings(user_id=u2.id, match_id=match1.id, module_id=2,
                                         weight=user2_match_specific_settings[1])
        mss3_2 = ModuleUserMatchSettings(user_id=u2.id, match_id=match1.id, module_id=3,
                                         weight=user2_match_specific_settings[2])

        db.session.add(mss1_1)
        db.session.add(mss2_1)
        db.session.add(mss3_1)
        db.session.add(mss1_2)
        db.session.add(mss2_2)
        db.session.add(mss3_2)
        db.session.commit()

        self.assertEqual(len(u1.list_match_specific_settings(match_id=match1.id)), 3,
                         "List user1 match specific settings contains 3 matches")

        for i in range(0, len(user1_match_specific_settings)):
            self.assertEqual(ModuleUserMatchSettings.query.filter_by(user_id=u1.id).all()[i].weight,
                             user1_match_specific_settings[i], "Check that user1 match specific weights are saved")

        self.assertIsNotNone(u2.list_match_specific_settings(match_id=match1.id),
                             "List user2 match specific settings contains 3 matches")

        for i in range(0, len(user2_match_specific_settings)):
            self.assertEqual(ModuleUserMatchSettings.query.filter_by(user_id=u2.id).all()[i].weight,
                             user2_match_specific_settings[i], "Check that user2 match specific weights are in saved")

        # make sure that different set of weights are used for two different users in the application
        probability_user_1 = match1.prediction_league_position * mss1_1.weight \
                           + match1.prediction_form * mss2_1.weight \
                           + match1.prediction_homeaway * mss3_1.weight

        self.assertAlmostEqual(probability_user_1, Match.predicted_winner(match1, u1).probability)

        probability_user2 = match1.prediction_league_position * mss1_2.weight \
                           + match1.prediction_form * mss2_2.weight \
                           + match1.prediction_homeaway * mss3_2.weight

        self.assertAlmostEqual(probability_user2, Match.predicted_winner(match1, u2).probability)

    def test_actual_winner(self):
        # ACTUAL WINNER
        # test a sample array of 3 played matches
        for m in self.u1.list_matches()[0:3]:
            if m.was_played:
                self.assertTrue(m.was_played, "The match was played")

                if m.match.hometeam_score > m.match.awayteam_score:
                    self.assertEqual(m.match.actual_winner, m.match.hometeam_id, 'Home win')
                elif m.match.hometeam_score < m.match.awayteam_score:
                    self.assertEqual(m.match.actual_winner, m.match.awayteam_id, 'Away win')
                else:
                    self.assertEqual(m.match.actual_winner, -1, 'It\'s a draw')

    def test_bettor_won(self):
        # BETTOR WON
        match3 = self.u1.list_matches()[0]
        match4 = self.u1.list_matches()[1]
        match3.committed = True
        match4.committed = True

        db.session.add(match3)
        db.session.add(match4)
        db.session.commit()

        for m in self.u1.list_matches()[0:2]:
            if Match.predicted_winner(user=self.u1,match=m.match).team_winner_id == m.match.actual_winner:
                # user guessed it correctly
                self.assertTrue(m.bettor_won, 'User predicted match result correctly')
            else:
                self.assertFalse(m.bettor_won, 'User has not predicted match result correctly')

        # change the settings so user predicts draw
        match_specific_settings = [0.6, 0.3, 0.1]

        mss1 = ModuleUserMatchSettings(user_id=self.u1.id, match_id=match4.match.id, module_id=1,
                                       weight=match_specific_settings[0])
        mss2 = ModuleUserMatchSettings(user_id=self.u1.id, match_id=match4.match.id, module_id=2,
                                       weight=match_specific_settings[1])
        mss3 = ModuleUserMatchSettings(user_id=self.u1.id, match_id=match4.match.id, module_id=3,
                                       weight=match_specific_settings[2])

        db.session.add(mss1)
        db.session.add(mss2)
        db.session.add(mss3)
        db.session.commit()

        for m in self.u1.list_matches()[0:2]:
            if Match.predicted_winner(user=self.u1,match=m.match).team_winner_id == m.match.actual_winner:
                # user guessed it correctly
                self.assertTrue(m.bettor_won, 'User predicted match result correctly')
            else:
                self.assertFalse(m.bettor_won, 'User has not predicted match result correctly')

    def test_user_hunch_module_contrib_to_draw(self):
        # TEST user hunch contrib to DRAW
        u1 = self.u1
        match1 = self.u1.list_matches()[0]
        match2 = self.u1.list_matches()[1]
        match1.committed = True
        match2.committed = True

        db.session.add(match1)
        db.session.add(match2)
        db.session.commit()

        match_specific_settings = [0.0, 0.0, 0.0, 1.0]

        mss1 = ModuleUserMatchSettings(user_id=u1.id, match_id=match1.match.id, module_id=1,
                                       weight=match_specific_settings[0])
        mss2 = ModuleUserMatchSettings(user_id=u1.id, match_id=match1.match.id, module_id=2,
                                       weight=match_specific_settings[1])
        mss3 = ModuleUserMatchSettings(user_id=u1.id, match_id=match1.match.id, module_id=3,
                                       weight=match_specific_settings[2])
        mss4 = ModuleUserMatchSettings(user_id=u1.id, match_id=match1.match.id, module_id=4,
                                       weight=match_specific_settings[3])

        db.session.add(mss1)
        db.session.add(mss2)
        db.session.add(mss3)
        db.session.add(mss4)
        db.session.commit()

        # module user hunch changed the result to draw
        self.assertEqual(Match.predicted_winner(match1.match, u1).team_winner_id, -1,
                         'User hunch contributed to Draw result')

    def test_user_hunch_module_contrib_to_change_result(self):
        # TEST user hunch contrib to DRAW, contrib to changing result
        # TEST user hunch contrib to DRAW
        prediction_result = ''
        u1 = self.u1
        match1 = self.u1.list_matches()[1]
        match2 = self.u1.list_matches()[1]
        match1.committed = True
        match2.committed = True

        db.session.add(match1)
        db.session.add(match2)
        db.session.commit()

        # module user hunch changed the result to draw
        if Match.predicted_winner(match1.match, u1).team_winner_id == match1.match.hometeam_id:
            # home win
            prediction_result = 1
        elif Match.predicted_winner(match1.match, u1).team_winner_id == match1.match.awayteam_id:
            # away win
            prediction_result = -1
        else:
            # draw
            prediction_result = 0

        match_specific_settings = [0.0, 0.0, 0.0, 1.0]

        mss1 = ModuleUserMatchSettings(user_id=u1.id, match_id=match1.match.id, module_id=1,
                                       weight=match_specific_settings[0])
        mss2 = ModuleUserMatchSettings(user_id=u1.id, match_id=match1.match.id, module_id=2,
                                       weight=match_specific_settings[1])
        mss3 = ModuleUserMatchSettings(user_id=u1.id, match_id=match1.match.id, module_id=3,
                                       weight=match_specific_settings[2])
        mss4 = ModuleUserMatchSettings(user_id=u1.id, match_id=match1.match.id, module_id=4,
                                       weight=match_specific_settings[3])

        db.session.add(mss1)
        db.session.add(mss2)
        db.session.add(mss3)
        db.session.add(mss4)
        db.session.commit()

        # module user hunch changed the result to draw
        if prediction_result == 1:
            match1.user_hunch = -100
            db.session.add(match1)
            db.session.commit()
            self.assertEqual(Match.predicted_winner(match1.match, u1, match1.user_hunch).team_winner_id,
                             match1.match.awayteam_id,
                             'User hunch changed the prediction')
        elif prediction_result == -1:
            match1.user_hunch = 100
            db.session.add(match1)
            db.session.commit()
            self.assertEqual(Match.predicted_winner(match1.match, u1, match1.user_hunch).team_winner_id,
                             match1.match.hometeam_id,
                             'User hunch changed the prediction')
        else:
            match1.user_hunch = 100
            db.session.add(match1)
            db.session.commit()
            self.assertEqual(Match.predicted_winner(match1.match, u1, match1.user_hunch).team_winner_id,
                             match1.match.hometeam_id,
                             'User hunch changed the prediction')