from pprint import pprint
import requests
import bs4

set_proxy_on = True
root_url = 'http://odds.bestbetting.com/'
index_url = root_url + 'football/england/premier-league/'

if set_proxy_on:
    http_proxy  = 'http://proxy.rgu.ac.uk:8080'
    https_proxy = 'https://proxy.rgu.ac.uk:8080'

    proxyDict = {
              'http'  : http_proxy,
              'https' : https_proxy
            }


response = requests.get(index_url, proxies=proxyDict)
soup = bs4.BeautifulSoup(response.text)
#matches = [a.attrs.get('href') for a in soup.select('div.video-summary-data a[href^=/video]')]
matches = soup.findAll("tr", { "class": "row0" })

def get_odds_data():
    odds_data = {}
    '''video_data['title'] = soup.select('div#videobox h3')[0].get_text()
    video_data['speakers'] = [a.get_text() for a in soup.select('div#sidebar a[href^=/speaker]')]
    video_data['youtube_url'] = soup.select('div#sidebar a[href^=http://www.youtube.com]')[0].get_text()'''



pprint (matches)

