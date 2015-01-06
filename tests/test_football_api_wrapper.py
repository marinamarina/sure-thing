#  python -m test discover
import unittest
from flask import current_app
from app import create_app, db
from pprint import pprint
from app.football_data.football_api_wrapper import FootballAPIWrapper

class TestFootballAPIWrapper(unittest.TestCase):
    def setUp(self):
        self.faw = FootballAPIWrapper()
        self.faw.api_key = '2890be06-81bd-b6d7-1dcb4b5983a0'

    @unittest.skip("To do")
    def test_get_beginning_year(self):
        pass

    @unittest.skip('')
    def test_unplayed_matches_tuple(self):
        from datetime import datetime
        matches = self.faw.unplayed_matches
        for m in matches:
            self.assertTrue(datetime.strptime(m.date, "%d.%m.%Y").date() >= datetime.now().date(),
                            "All the matches dates should be IN THE FUTURE compared to today")
            self.assertTrue(m.ft_score == '', 'FT Score is unknown=>match has not been played yet')

    @unittest.skip('')
    def test_played_matches_tuple(self):
        from datetime import datetime
        matches = self.faw.played_matches
        for m in matches:
            self.assertTrue(datetime.strptime(m.date, "%d.%m.%Y").date() <= datetime.now().date(),
                            "All the matches dates should be IN THE PAST compared to today")

    @unittest.skip('')
    def test_standings(self):
        league_table = self.faw.league_table
        print ("\n")
        self.assertEqual(len(league_table.items()), 20 , 'There are 20 teams in the premier league')

        for team_id, tuple in league_table.items():
            print team_id, tuple.position

    def test_league_table(self):
        league_table = self.faw.league_table
        print ("\n")

        from pprint import pprint
        pprint(league_table)

    def test_unplayed_matches_tuple(self):
        pprint(self.faw.form_and_tendency(9002))