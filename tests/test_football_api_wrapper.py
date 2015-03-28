#  python -m test discover
import unittest
from datetime import datetime
import os.path
import shutil
from app.football_data.football_api_wrapper import FootballAPIWrapper


@unittest.skip("skipping due to the time delay")
class TestFootballAPIWrapper(unittest.TestCase):
    """Testing the Football API Wrapper
        Note that private methods are tested throught the public interface (public methods)

    """
    @classmethod
    def setUpClass(cls):
        cls.faw = FootballAPIWrapper()
        # data directory for testing purposes
        datadir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app/data_test'))
        cls.faw.datadir = datadir

        if not os.path.exists(datadir):
            os.makedirs(datadir)

        cls.faw.api_key = '2890be06-81bd-b6d7-1dcb4b5983a0'
        cls.faw.write_matches_data()
        cls.faw.write_standings_data()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.faw.datadir)
        cls.faw = None

    def test_write_matches_data(self):
        base_filename = 'all_matches'
        filename_suffix = 'json'
        filename = os.path.join(self.faw.datadir, base_filename + "." + filename_suffix)

        os.path.isfile(filename)

    def test_write_standings_data(self):
        base_filename = 'standings'
        filename_suffix = 'json'
        filename = os.path.join(self.faw.datadir, base_filename + "." + filename_suffix)

        os.path.isfile(filename)

    # test static methods
    def test_get_beginning_year(self):
        pass

    def test_get_end_year(self):
        pass

    def test_api_key(self):
        # create a new instance with no api key assigned
        faw = FootballAPIWrapper()
        with self.assertRaises(AttributeError):
            faw.api_key

    def test_data_dir(self):
        pass

    def test_form_and_tendency(self):
        pass

    def test_ids_names(self):
        ids_names = self.faw.ids_names
        self.assertEqual(len(ids_names), 20, 'English Premier League has 20 teams')
        self.assertEqual(ids_names[9221], 'Hull City', 'Checking that the id associates with a certain team')

    def test_all_matches(self):
        all_matches = self.faw.all_matches
        self.assertIs(type(all_matches), list, 'All matches is a list')
        self.assertFalse(all_matches[0].hometeam_score == '?', 'The first match was played and has a full time score')
        #print all_matches[len(all_matches)-1]

    def test_unplayed_matches(self):
        unplayed_matches = self.faw.unplayed_matches
        self.assertIs(type(unplayed_matches), list, 'Unplayed matches is a list')

        # check that each match in the list is unplayed
        for um in unplayed_matches:
            self.assertFalse(um.hometeam_score != '?', 'Each match in the list was not played'
                                                       ' and does not have a full time score')
            self.assertTrue(datetime.strptime(um.date, "%d.%m.%Y").date() >= datetime.now().date(),
                            "All the matches dates should be IN THE FUTURE compared to today")
            self.assertTrue(um.ft_score == '', 'FT Score is unknown=>match has not been played yet')

    def test_played_matches(self):
        played_matches = self.faw.played_matches
        self.assertIs(type(played_matches), list, 'Played matches is a list')

        # each match in the list is played
        for pm in played_matches:
            self.assertFalse(pm.hometeam_score == '?', 'Each match in the list was played'
                                                       ' and has a full time score')
            self.assertTrue(datetime.strptime(pm.date, "%d.%m.%Y").date() <= datetime.now().date(),
                            "All the matches dates should be IN THE PAST compared to today")

    def test_league_table(self):
        league_table = self.faw.league_table
        print ("\n")
        self.assertEqual(len(league_table.items()), 20 , 'There are 20 teams in the premier league')

    def test_date_tuple(self):
        pass