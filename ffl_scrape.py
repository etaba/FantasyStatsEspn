from bs4 import BeautifulSoup
import requests
from collections import namedtuple
from pprint import pprint
import json, sys

COOKIES = {'SWID': '{7C03F19F-1221-43BB-83F1-9F122153BB1C}',
           'espn_s2': 'AEAGgxIKhbIj92Bc830dkd2Bp5o2B1%2F3KpRmlnSZfXK9zI73s7F3WSYmNu%2BEWLMXkwoQ5V1YSiBCyzo%2FjnnMFkQO5MzgKjp5Ug652%2B4TVjIfSufSfCI99MFltq%2B2qRvCO4j3KNC5kioST5PC1%2FseTjod5IRt2y7n2ZKGbd2sa%2BlKWJkboAJN3zmuZGUJetuB%2B6Zt4L%2BGs%2BRNHUqEunVmw8zTp%2FZiUd0dMGWNci5KSqTAyaNK3potC%2F88bDQNVJDVnd0I4%2BlqvcQt1IhtF1O%2BHMUA'}

TEAMS = { team:id for team,id in zip(['Erick Pirayesh','Dylan Meyer','Tyler Stone','Steve Meyer','Eric Davis','Matt McDonald','Sean  McDonald','Steven Asire','Codey Harrison','Tyler Moore','Jon Fankhauser','luke ceverha','eric taba','jonathan  zerna'],range(1,15))}
LEAGUE = '977855'



#get schedule:
#schedule = {<int>week: 
#						[Match(away,home)]}
Match = namedtuple('Match','away home')
r = requests.get(f'https://fantasy.espn.com/football/league/schedule?leagueId={LEAGUE}',cookies=COOKIES)
soup = BeautifulSoup(r.content, 'html.parser')
print(r.content)
sys.exit()
table = soup.find('table', class_='tableBody')
schedule = { i:[] for i in range(1,14)}
week = 0
for tr in table.find_all('tr'):
	if tr['bgcolor'] == '#1d7225':
	# if 'class' in tr and 'tableSubHead' in tr['class']:
		week += 1
		if week > 13:
			break
	elif tr['bgcolor'] == '#f2f2e8' or tr['bgcolor'] == '#f8f8f2':
		tds = tr.find_all('td')
		away_team = tds[1].text
		home_team = tds[4].text
		schedule[week].append(Match(away_team,home_team))


#get every team's week breakdown
lineups = { team:{ week:{'lineup':[],'bench':[]} for week in range(1,14)} for team in TEAMS.keys() }
for week in range(1,14):
	for team in TEAMS.keys():
		url = f'http://games.espn.com/ffl/boxscorequick?leagueId={LEAGUE}&teamId={TEAMS[team]}&scoringPeriodId={week}&seasonId=2018&view=scoringperiod&version=quick'
		r = requests.get(url,cookies=COOKIES)
		soup = BeautifulSoup(r.content, 'html.parser')
		#get lineup
		table = soup.find('table', id='playertable_0')
		for tr in table.find_all('tr',class_='pncPlayerRow'):
			tds = tr.find_all('td')
			slot = tds[0].text
			try:
				player = tds[1].find('a').text
				player_info = tds[1].find(text=True,recursive=False)
				if 'D/ST' in player_info:
					player_pos = 'D/ST'
				else:
					player_pos = ''.join(player_info.split()[2:])
				if len(tds) == 5:
					points = float(tds[4].text) if tds[4].text != '--' else 0
				else:
					points = float(tds[3].text) if tds[3].text != '--' else 0
			except Exception:
				player = ''
				player_pos = ''
				points = 0
			lineups[team][week]['lineup'].append({'slot':slot,'player':player,'player_pos':player_pos,'points':points})
		#get bench
		table = soup.find('table', id='playertable_1')
		for tr in table.find_all('tr',class_='pncPlayerRow'):
			tds = tr.find_all('td')
			try:
				player = tds[1].find('a').text
				player_info = tds[1].find(text=True,recursive=False)
				if 'D/ST' in player_info:
					player_pos = 'D/ST'
				else:
					player_pos = ''.join(player_info.split()[2:])
				if len(tds) == 5:
					points = float(tds[4].text) if tds[4].text != '--' else 0
				else:
					points = float(tds[3].text) if tds[3].text != '--' else 0
				lineups[team][week]['bench'].append({'slot':slot,'player':player,'player_pos':player_pos,'points':points})
			except Exception:
				pass
with open('ffl_work_2018.json','w+') as f:
	json.dump({'schedule':schedule,'lineups':lineups},f)