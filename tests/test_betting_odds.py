#  python -m test discover
import unittest
from pprint import pprint
from app.football_data.football_api_wrapper import FootballAPIWrapper

class TestFootballAPIWrapper(unittest.TestCase):
    def setUp(self):
        self.faw = FootballAPIWrapper()
        self.faw.api_key = '2890be06-81bd-b6d7-1dcb4b5983a0'

    def test_scraper(self):
        pass