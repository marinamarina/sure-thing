#  python -m test discover
import unittest
from flask import current_app
from app import create_app, db
from pprint import pprint
from app.football_data.football_api_wrapper import FootballAPIWrapper

class FootballAPIWrapper(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        faw = FootballAPIWrapper()
        faw.api_key = '2890be06-81bd-b6d7-1dcb4b5983a0'
        #set the api key
        #self.wrap.api_key = '2890be06-81bd-b6d7-1dcb4b5983a0'

        #pprint(self.wrap.all_and_unplayed_matches.unplayed)

    def test_get_beginning_year(self):
        pass

    def test_feed_all_and_unplayed_matches(self):
        self.assertTrue(1==1)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()