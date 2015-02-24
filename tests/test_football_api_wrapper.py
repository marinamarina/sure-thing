#  python -m test discover
import unittest
from flask import current_app
from datetime import datetime
from pprint import pprint
from app.football_data.football_api_wrapper import FootballAPIWrapper

class TestFootballAPIWrapper(unittest.TestCase):
    def setUp(self):
        self.faw = FootballAPIWrapper()
        self.faw.api_key = '2890be06-81bd-b6d7-1dcb4b5983a0'

    @unittest.skip("To do")
    def test_get_beginning_year(self):
        pass

    def test_all_matches(self):
        print('\n----ALL MATCHES---')
        matches = self.faw.all_matches
        for m in matches:
            print m

    def test_unplayed_matches_tuple(self):
        matches = self.faw.unplayed_matches
        for m in matches:
            self.assertTrue(datetime.strptime(m.date, "%d.%m.%Y").date() >= datetime.now().date(),
                            "All the matches dates should be IN THE FUTURE compared to today")
            self.assertTrue(m.ft_score == '', 'FT Score is unknown=>match has not been played yet')

    def test_played_matches_tuple(self):
        matches = self.faw.played_matches
        for m in matches:
            self.assertTrue(datetime.strptime(m.date, "%d.%m.%Y").date() <= datetime.now().date(),
                            "All the matches dates should be IN THE PAST compared to today")

    def test_standings(self):
        league_table = self.faw.league_table
        print ("\n")
        self.assertEqual(len(league_table.items()), 20 , 'There are 20 teams in the premier league')


    def test_unplayed_matches_tuple(self):
        pprint(self.faw.form_and_tendency(9002))