#! usr/bin/python

import urllib2
import json
from datetime import datetime
from collections import namedtuple, OrderedDict
import urllib

'''
    TODO: switch to API version 2
    http://api2.football-api.com/api/?Action=team&APIKey=[YOUR_API_KEY]&team_id=[team]
'''
class FootballAPIWrapper:
    def __init__(self, methodName='runTest'):
        '''self.app = app
        if app is not None:
            self.init_app(app)'''

        self.__premier_league_id = '1204'
        self.__base_url = 'http://football-api.com/api/?Action='
        self.proxy_on = False

    def init_app(self, app):
        '''if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)'''
        pass

    @staticmethod
    def get_beginning_year(current_month, current_year):
        'checking in which year the season began'
        if current_month > 7:
            season_began_in_year = current_year
        else:
            season_began_in_year = current_year - 1
        return season_began_in_year

    @staticmethod
    def get_end_year(current_month, current_year):
        'checking in which year the season began'
        if current_month > 7:
            season_ends_in_year = current_year + 1
        else:
            season_ends_in_year = current_year
        return season_ends_in_year


    def call_api(self, action=None, **kwargs):
        """ Call the Football API
        :param action: Football API action: competition, standings, today, fixtures, commentaries
        :param kwargs: e.g
        :return: output as a json object
        :raise (Exception('Error: Action was not passed')):
        """
        if action is None:
            raise(Exception('Error: Action not passed to call_api'))

        # use ordered dictionary, so API key is always in the beginning

        params = OrderedDict()
        output_data = dict()

        params['APIKey'] = self.api_key

        for kwarg in kwargs:
            params[kwarg] = kwargs[kwarg]

        url = self.__base_url \
               + action \
               + '&comp_id=' + self.__premier_league_id

        params = urllib.urlencode(params)
        print ("My url {}").format(url + '&%s' % params)

        try:
            if (self.proxy_on):
                proxy = urllib2.ProxyHandler({'http': 'http://proxy1.rgu.ac.uk:8080'})
                opener = urllib2.build_opener(proxy)
                urllib2.install_opener(opener)

            my_json = urllib2.urlopen(url + '&%s' % params)
        except urllib2.URLError, e:
            print 'URL error: ' + str(e.reason)
        except Exception:
            print 'Other exception'
        else:
            output_data = json.load(my_json)

        return output_data

    def feed_ids_names(self):
        """Create an team id -> name relationship"""
        with open(self.data_dir + '/standings.json', 'r') as localfile:
            standings_data = json.load(localfile)
        localfile.close()

        # feeding the dictionary
        output_data = {
            int(team["stand_team_id"]) : team["stand_team_name"]
            for team in standings_data['standings']
        }

        return output_data

    def get_all_matches(self):
        """Get the matches json from an API"""
        action = 'fixtures'
        params = {'from_date': '01.08.' + str(self.date_tuple.beginning_year), 'to_date' : '31.05.' + str(self.date_tuple.end_year)}
        all_matches = self.call_api(action, **params)
        return all_matches

    def get_standings(self):
        'Get the standings json from the API'
        action = 'standings'
        data_standings = self.call_api(action)
        return data_standings

    def write_matches_data (self):
        'Write matches json to the local file'
        raw_data = dict()
        try:
            raw_data["matches"] = self.get_all_matches()["matches"]
            raw_data["date-time"] = self.date_tuple.today + ' ' + self.date_tuple.current_time

            with open(self.data_dir + '/all_matches.json', mode = 'w') as outfile:
                json.dump(raw_data, outfile)

            outfile.close()
            print ('matches updated!')
        except KeyError:
            print ('*********Please, update your IP address!*********')


    def write_standings_data (self):
        """Write standings json to the local file"""
        raw_data = dict()

        try:
            raw_data["standings"] = self.get_standings()["teams"]
            raw_data["date-time"] = self.date_tuple.today + ' ' + self.date_tuple.current_time

            with open(self.data_dir + '/standings.json', mode = 'w') as outfile:
                json.dump(raw_data, outfile)

            outfile.close()
            print ('league table data updated!')

        except KeyError:
            print ('********Please, update your IP address!********')


    def feed_all_and_unplayed_matches(self):
        """
        Create a named tuple with all matches for the season
        Read the data from a local file
        :return tuple of two arrays of tuples
        """

        with open(self.data_dir + '/all_matches.json', 'r') as localfile:
            matches_data = json.load(localfile)
        localfile.close()

        MatchInfo = namedtuple('MatchInfo',
                               'id date time date_stamp time_stamp '
                               'hometeam_id awayteam_id '
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


    def feed_league_table(self):
        '''
        Create a dictionary with the current standings
        Read the data from a local file
        :return league_table dictionary
        '''
        with open(self.data_dir + '/standings.json', 'r') as localfile:
            standings_data = json.load(localfile)
        localfile.close()
        league_table = OrderedDict()
        TeamInfo = namedtuple('TeamInfo', 'position team_name matches_played w d l goals_for goals_against gp points form')


        league_table = {team['stand_team_id'] : TeamInfo(team['stand_position'], team['stand_team_name'], team['stand_round'],
                        team['stand_overall_w'], team['stand_overall_d'], team['stand_overall_l'],
                        team['stand_overall_gs'], team['stand_overall_ga'], team['stand_gd'], team['stand_points'], team['stand_recent_form'])

                        for team in standings_data['standings']
            }

        return league_table

    def form_and_tendency(self, id):
        """I need to output all matches played by the team (tendency and result)
        structure of the returned data:
        team_id: [MatchForFormInfo(id,date,time,hometeam, awayteam,homescore, awayscore,outcome),()...]
        """

        all_played_matches = self.played_matches
        form_and_tendency_data = dict()
        MatchForFormInfo = namedtuple('MatchForFormInfo', 'id, date_stamp, time_stamp, hometeam_id, awayteam_id,'
                                                          'hometeam_score, awayteam_score, outcome')

        # loop through the team ids
        for team_id in self.ids_names:

            #empty the matches list
            matches_list = []

            # loop through the matches and pick the right ones
            for match in all_played_matches:
                if team_id==match.hometeam_id or team_id==match.awayteam_id:

                    if team_id == match.hometeam_id:
                        team_is_at_home = True
                    elif team_id == match.awayteam_id:
                        team_is_at_home = False

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
                        match.time_stamp,
                        match.hometeam_id,
                        match.awayteam_id,
                        int(match.hometeam_score),
                        int(match.awayteam_score),
                        outcome
                    )

                    matches_list.append(matchForFormInfo)

            form_and_tendency_data[team_id] = matches_list[::-1]

        # we can output either the whole data set or just a line for a particular team
        if id is None:
            return form_and_tendency_data
        else:
            return form_and_tendency_data[id]

    @property
    def api_key(self):
        raise AttributeError('API is a non-readable attribute!')

    @api_key.setter
    def api_key(self, value):
        self.api_key = value

    @property
    def data_dir(self):
        return 'app/data'

    @data_dir.setter
    def data_dir(self, value):
        self.data_dir = value

    @property
    def ids_names(self):
        self.ids_names = self.feed_ids_names()
        return self.ids_names

    @property
    def all_matches(self):
        self.all_matches = self.feed_all_and_unplayed_matches().all
        return self.all_matches

    @property
    def unplayed_matches(self):
        self.unplayed_matches = self.feed_all_and_unplayed_matches().unplayed
        return self.unplayed_matches

    @property
    def played_matches(self):
        self.played_matches = self.feed_all_and_unplayed_matches().played
        return self.played_matches

    @property
    def date_tuple(self):
        today = datetime.now()
        today_formatted = today.strftime("%d.%m.%Y")
        current_time = today.strftime("%H:%M")

        beginning_year = self.get_beginning_year(today.month, today.year)
        end_year = self.get_end_year(today.month, today.year)

        Dates = namedtuple("Dates", "today current_time month beginning_year end_year")
        return Dates(today_formatted, current_time, today.month, beginning_year, end_year)

    @property
    def league_table(self):
        self.league_table = self.feed_league_table()
        return self.league_table