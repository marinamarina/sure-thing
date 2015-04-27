import re
import unittest
from flask import url_for
from app import create_app, db
from app.models import User, Role, Match
import bs4


class AuthenticationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index_page(self):
        response = self.client.get(url_for('main.index'))
        self.assertTrue(b'LOG IN' in response.data)

    def test_matches(self):
        response = self.client.get(url_for('main.index'))
        soup = bs4.BeautifulSoup(response.data)
        matches = soup.select('div.match')
        self.assertGreater(len(matches), 0)




