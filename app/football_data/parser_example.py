#! usr/bin/python
from football_api_parser import FootballAPIWrapper
from pprint import pprint

# example usage
wrap = FootballAPIWrapper()

# set the api key
wrap.api_key = '2890be06-81bd-b6d7-1dcb4b5983a0'

dict1 = dict()
ids_dict = {'Manchester': 1, 'Aston Villa': 3}

pprint (wrap.league_table)