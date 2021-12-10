from bs4 import BeautifulSoup
from collections import defaultdict
import pandas as pd
import pickle
import requests
from unidecode import unidecode

# this dictionary will map players to a set containing all the years in which they were selected for an all-star game, either initially or as a replacement
dpoy = defaultdict(set)

# rows to ignore when iterating the roster tables
ignore_fields = set(['Team Totals', 'Reserves'])

 # unidecode doesn't catch the accented c in Peja's last name (Stojakovic), fix it
 # also overwrite any instance of Metta World Peace to Ron Artest
def fix_name(full_name):
	first_name = full_name.split(' ')[0]
	if first_name == 'Peja':
		return 'Peja Stojakovic'
	elif first_name == 'Metta':
		return 'Ron Artest'
	else:
		return unidecode(full_name)


print('Scraping ASG {} data...')

# will store all the all-stars for this year
dpoys = set([])

html = requests.get('https://www.basketball-reference.com/awards/dpoy.html').content
soup = BeautifulSoup(html, 'html.parser')

# this part was annoying - back when ASG was always East vs. West, the tables were encoded with id="East"/id="West" so they could be extracted more easily/reliably
# but now, you have games like Giannis vs. LeBron and the table id's are different, so I had to extract them by index, which is unreliable in the event that the 
# site's design changes in the future

# gets rosters for team 1 and team 2
s1 = soup.findAll('table')[1]

df1 = pd.read_html(str(s1))[0]

# get the all-stars from teams 1 and 2
for df in [df1]:
	for i, row in df.iterrows():
		if pd.notnull(row[0]) and row[0] not in ignore_fields:
			player = row[0]
			dpoys.add(fix_name(player))

# update the appearances dictionary
for player in dpoys:
	dpoy[player].add(year)

sorted_dpoy = sorted([(player, sorted(list(appearances))) for player, appearances in dpoy.items()], key = lambda x : -len(x[1]))

print('\nAll all-star appearances since 1970 (sorted by number of appearances):\n')

for player, appearances in sorted_dpoy:
	print('{}: {}'.format(player, appearances))

# export the dictionary to local disk for future recall in statsnba_fullscrape.py
out = open('dpoy.pickle', 'wb')
pickle.dump(dpoy, out)
out.close