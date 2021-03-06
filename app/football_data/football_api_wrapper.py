#! usr/bin/python

import json
from datetime import datetime
from collections import namedtuple, OrderedDict
import urllib
import requests
import os
'''
    TODO: switch to API version 2
    http://api2.football-api.com/api/?Action=team&APIKey=[YOUR_API_KEY]&team_id=[team]
'''


class FootballAPIWrapper:
    def __init__(self):
        self._premier_league_id = '1204'
        self._base_url = 'http://football-api.com/api/?Action='
        self._basedir = os.path.dirname(__file__)
        self._datadir = os.path.abspath(os.path.join(self._basedir, '..', 'data'))
        self._proxy_on = True

    def _call_api(self, action=None, **kwargs):
        """
        Store the response from the search endpoint in json_response
        :param action: Football API action: competition, standings, today, fixtures, commentaries
        :param kwargs: e.g
        :return: output as a json object
        :raise (Exception('Error: Action was not passed')):
        """
        json_response = {}
        if action is None:
            raise(Exception('Error: Action not passed to call_api'))

        # use ordered dictionary, so API key is always in the beginning

        params = OrderedDict()

        params['APIKey'] = self.api_key

        for kwarg in kwargs:
            params[kwarg] = kwargs[kwarg]

        url = self._base_url \
            + action \
            + '&comp_id=' + self._premier_league_id

        params = urllib.urlencode(params)
        print "My url {}".format(url + '&%s' % params)

        if self._proxy_on:
            http_proxy = {
                "http": "http://1014481:password@proxy1.rgu.ac.uk:8080/"
            }
        else:
            http_proxy = {}

        try:
            response = requests.get(url=url + '&%s' % params, proxies=http_proxy)
            json_response = response.json()
        except requests.exceptions.ConnectionError:
            print ("These aren't the domains we're looking for.")
        except requests.exceptions.HTTPError as e:
            print ("A HTTP error occured:", e.message)

        return json_response

    def _get_all_matches(self):
        """Get the matches json response from an API"""
        action = 'fixtures'
        params = {'from_date': '01.08.' + str(self.date_tuple.beginning_year), 'to_date' : '31.05.' + str(self.date_tuple.end_year)}
        all_matches = self._call_api(action, **params)
        return all_matches

    def _get_standings(self):
        """Get the standings json response from the API"""
        action = 'standings'
        data_standings = self._call_api(action)
        return data_standings

    def write_standings_data(self):
        """Write standings json response to the local file"""
        print('\n-----WRITING STANDINGS----')

        raw_data = dict()

        try:
            raw_data["standings"] = self._get_standings()["teams"]
            raw_data["date-time"] = self.date_tuple.today + ' ' + self.date_tuple.current_time

            with open(self.datadir + '/standings.json', mode='w') as outfile:
                json.dump(raw_data, outfile)

            outfile.close()
            print ('league table data updated!')

        except KeyError:
            print ('********Please, update your IP address!********')

    def write_matches_data(self):
        """Write matches json response to the local file"""
        print('\n-----WRITING MATCHES----')

        raw_data = dict()
        try:
            raw_data["matches"] = self._get_all_matches()["matches"]
            raw_data["date-time"] = self.date_tuple.today + ' ' + self.date_tuple.current_time

            with open(self.datadir + '/test.txt', 'wb') as localfile:
                localfile.write("Keekaboos")
            localfile.close()

            with open(self.datadir + '/all_matches.json', mode='w') as outfile:
                json.dump(raw_data, outfile)

            outfile.close()
        except KeyError:
            print ('*********Please, update your IP address!*********')

    def _feed_ids_names(self):
        """Create an team id -> name relationship
            that can be accessed via property
        """
        with open(self.datadir + '/standings.json', 'r') as localfile:
            standings_data = json.load(localfile)
        localfile.close()

        # feeding the dictionary
        output_data = {
            int(team["stand_team_id"]): team["stand_team_name"]
            for team in standings_data['standings']
        }

        return output_data

    def _feed_all_and_unplayed_matches(self):
        """
        Create a named tuple with all matches for the season
        Read the data from a local file
        :return tuple of two arrays of tuples
        """

        with open(self.datadir + '/all_matches.json', 'r') as localfile:
            matches_data = json.load(localfile)
            from pprint import pprint
        localfile.close()

        MatchInfo = namedtuple('MatchInfo',
                               'id date time date_stamp time_stamp '
                               'hometeam_id awayteam_id '
                               'hometeam_name awayteam_name '
                               'hometeam_score awayteam_score '
                               'ft_score')
        all_matches = []
        unplayed_matches = []
        played_matches = []
        MatchesAllAndUnplayed = namedtuple('MatchesAllAndUnplayed', 'all unplayed played')

        for m in matches_data["matches"]:
            matchInfo = MatchInfo(int(m['match_id']),
                                  m['match_formatted_date'],
                                  m['match_time'],
                                  datetime.strptime(m['match_formatted_date'], "%d.%m.%Y").date(),
                                  datetime.strptime(m['match_time'], "%H:%M").time(),
                                  int(m['match_localteam_id']),
                                  int(m['match_visitorteam_id']),
                                  m['match_localteam_name'],
                                  m['match_visitorteam_name'],
                                  m['match_localteam_score'],
                                  m['match_visitorteam_score'],
                                  m['match_ft_score']
            )

            all_matches.append(matchInfo)

            if matchInfo.ft_score == '':
                unplayed_matches.append(matchInfo)
            else:
                played_matches.append(matchInfo)

        return MatchesAllAndUnplayed(all_matches, unplayed_matches, played_matches)

    def _feed_league_table(self):
        """
        Create a dictionary with the current standings
        Read the data from a local file
        :return league_table dictionary
        """
        with open(self.datadir + '/standings.json', 'r') as localfile:
            standings_data = json.load(localfile)

        localfile.close()
        TeamInfo = namedtuple('TeamInfo', 'position team_name matches_played w d l goals_for goals_against gp points form')

        league_table = OrderedDict({team['stand_team_id'] : TeamInfo(team['stand_position'], team['stand_team_name'], team['stand_round'],
                        team['stand_overall_w'], team['stand_overall_d'], team['stand_overall_l'],
                        team['stand_overall_gs'], team['stand_overall_ga'], team['stand_gd'], team['stand_points'], team['stand_recent_form'])

                        for team in standings_data['standings']
            })

        return league_table

    def form_and_tendency(self, id):
        """I need to output all matches played by the team (tendency and result)
            structure of the returned data:
            team_id: [MatchForFormInfo(id,date,time,hometeam, awayteam,homescore, awayscore,outcome),()...]
            This is a method, not a property, because we pass a parameter in
        """

        all_played_matches = self.played_matches
        form_and_tendency_data = dict()
        MatchForFormInfo = namedtuple('MatchForFormInfo', 'id, date_stamp, date, time_stamp, hometeam_id, awayteam_id,'
                                                          'hometeam_name, awayteam_name hometeam_score, awayteam_score,'
                                                          ' opponent_id, opponent_name, outcome, home')

        # loop through the team ids
        for team_id in self.ids_names:

            #empty the matches list
            matches_list = []

            # loop through the matches and pick the right ones
            for match in all_played_matches:
                if team_id == match.hometeam_id or team_id == match.awayteam_id:

                    if team_id == match.hometeam_id:
                        team_is_at_home = True
                        #opponent is awayteam
                        opponent_id = match.awayteam_id
                        opponent_name = match.awayteam_name

                    elif team_id == match.awayteam_id:
                        team_is_at_home = False
                        opponent_id = match.hometeam_id
                        opponent_name = match.hometeam_name

                    if team_is_at_home and match.hometeam_score > match.awayteam_score or  \
                        not team_is_at_home and match.hometeam_score < match.awayteam_score:
                            outcome = 'W'
                    elif match.hometeam_score == match.awayteam_score:
                        outcome = 'D'
                    else:
                        outcome = 'L'

                    # create a tuple representing a match
                    matchForFormInfo = MatchForFormInfo(
                        match.id,
                        match.date_stamp,
                        match.date,
                        match.time_stamp,
                        match.hometeam_id,
                        match.awayteam_id,
                        match.hometeam_name,
                        match.awayteam_name,
                        int(match.hometeam_score),
                        int(match.awayteam_score),
                        opponent_id,
                        opponent_name,
                        outcome,
                        team_is_at_home
                    )

                    matches_list.append(matchForFormInfo)

            form_and_tendency_data[team_id] = matches_list[::-1]

        return form_and_tendency_data[id]

    @staticmethod
    def get_beginning_year(current_month, current_year):
        """checking in which year the season began"""
        if current_month > 7:
            season_began_in_year = current_year
        else:
            season_began_in_year = current_year - 1
        return season_began_in_year

    @staticmethod
    def get_end_year(current_month, current_year):
        """checking in which year the season began"""
        if current_month > 7:
            season_ends_in_year = current_year + 1
        else:
            season_ends_in_year = current_year
        return season_ends_in_year


    @property
    def api_key(self):
        """Read-only property!"""
        raise AttributeError('API is a non-readable attribute!')

    @api_key.setter
    def api_key(self, value):
        self.api_key = value

    @property
    def datadir(self):
        return self._datadir

    @datadir.setter
    def datadir(self, path):
        self.datadir = path

    @property
    def ids_names(self):
        return self._feed_ids_names()

    @property
    def all_matches(self):
        return self._feed_all_and_unplayed_matches().all

    @property
    def unplayed_matches(self):
        return self._feed_all_and_unplayed_matches().unplayed

    @property
    def played_matches(self):
        return self._feed_all_and_unplayed_matches().played

    @property
    def league_table(self):
        return self._feed_league_table()

    @property
    def date_tuple(self):
        today = datetime.now()
        today_formatted = today.strftime("%d.%m.%Y")
        current_time = today.strftime("%H:%M")

        beginning_year = self.get_beginning_year(today.month, today.year)
        end_year = self.get_end_year(today.month, today.year)

        Dates = namedtuple("Dates", "today current_time month beginning_year end_year")
        return Dates(today_formatted, current_time, today.month, beginning_year, end_year)
