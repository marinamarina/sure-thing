import unittest
import time
from datetime import datetime
from app import create_app, db
from app.models import User, AnonymousUser, Role, Permission, Follow


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.u = User(password='cat')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        self.assertTrue(self.u.password_hash is not None)

    def test_password_is_read_only(self):
        with self.assertRaises(AttributeError):
            self.u.password

    def test_password_verification(self):
        self.assertTrue(self.u.verify_password('cat'))
        self.assertFalse(self.u.verify_password('car'))

    def test_password_salts_are_random(self):
        # add another user
        u2 = User(password='cat')
        self.assertTrue(self.u.password_hash != u2.password_hash)