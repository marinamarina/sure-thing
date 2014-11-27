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

        #set the api key
        #self.wrap.api_key = '2890be06-81bd-b6d7-1dcb4b5983a0'

        #pprint(self.wrap.all_and_unplayed_matches.unplayed)

    @unittest.skip("To do")
    def test_get_beginning_year(self):
        pass

    def test_unplayed_matches_tuple(self):
        from datetime import datetime
        matches = self.faw.unplayed_matches
        for m in matches:
            self.assertTrue(datetime.strptime(m.date, "%d.%m.%Y").date() >= datetime.now().date(),
                            "All the matches dates should be IN THE FUTURE compared to today")

    def test_played_matches_tuple(self):
        from datetime import datetime
        matches = self.faw.played_matches
        for m in matches:
            self.assertTrue(datetime.strptime(m.date, "%d.%m.%Y").date() <= datetime.now().date(),
                            "All the matches dates should be IN THE PAST compared to today")


