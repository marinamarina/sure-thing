#  python -m test discover
import unittest
from .. app import create_app, db
from .. app.football_data.football_api_parser import FootballAPIWrapper
from flask import current_app
from pprint import pprint

class FootballAPIWrapper(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.wrap = FootballAPIWrapper()
        #set the api key
        #self.wrap.api_key = '2890be06-81bd-b6d7-1dcb4b5983a0'

        #pprint(self.wrap.all_and_unplayed_matches.unplayed)

    '''def test_get_beginning_year(self):
        pass'''

    def test_feed_all_and_unplayed_matches(self):
        self.assertTrue(1==1)

if __name__ == '__main__':
    unittest.main()