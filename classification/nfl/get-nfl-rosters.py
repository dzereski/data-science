"""
get-nfl-rosters
~~~~~~~~~~~~~~~~
Get basic stats on all current NFL players
"""

from __future__ import print_function
import time
import re
import unicodecsv as csv

import requests
from bs4 import BeautifulSoup


def main():
    team_rosters = {
        'Cardinals': 'https://www.azcardinals.com/team/players-roster/',
        'Falcons': 'https://www.atlantafalcons.com/team/players-roster/',
        'Ravens': 'https://www.baltimoreravens.com/team/players-roster/',
        'Bills': 'https://www.buffalobills.com/team/players-roster/',
        'Panthers': 'https://www.panthers.com/team/players-roster/',
        'Bears': 'https://www.chicagobears.com/team/players-roster/',
        'Bengals': 'https://www.bengals.com/team/players-roster/',
        'Browns': 'https://www.clevelandbrowns.com/team/players-roster/',
        'Cowboys': 'https://www.dallascowboys.com/team/players-roster/',
        'Broncos': 'https://www.denverbroncos.com/team/players-roster/',
        'Lions': 'https://www.detroitlions.com/team/players-roster/',
        'Packers': 'https://www.packers.com/team/players-roster/',
        'Texans': 'https://www.houstontexans.com/team/players-roster/',
        'Colts': 'https://www.colts.com/team/players-roster/',
        'Jaguars': 'https://www.jaguars.com/team/players-roster/',
        'Chiefs': 'https://www.chiefs.com/team/players-roster/',
        'Chargers': 'https://www.chargers.com/team/players-roster/',
        'Rams': 'https://www.therams.com/team/players-roster/',
        'Dolphins': 'https://www.miamidolphins.com/team/players-roster/',
        'Vikings': 'https://www.vikings.com/team/players-roster/',
        'Patriots': 'https://www.patriots.com/team/players-roster/',
        'Saints': 'https://www.neworleanssaints.com/team/players-roster/',
        'Giants': 'https://www.giants.com/team/players-roster/',
        'Jets': 'https://www.newyorkjets.com/team/players-roster/',
        'Raiders': 'https://www.raiders.com/team/players-roster/',
        'Eagles': 'https://www.philadelphiaeagles.com/team/players-roster/',
        'Steelers': 'https://www.steelers.com/team/players-roster/',
        '49ers': 'https://www.49ers.com/team/players-roster/',
        'Seahawks': 'https://www.seahawks.com/team/players-roster/',
        'Buccaneers': 'https://www.buccaneers.com/team/players-roster/',
        'Titans': 'https://www.titansonline.com/team/players-roster/',
        'Redskins': 'https://www.redskins.com/team/players-roster/'
    }

    # Regex to find player height and convert to inches
    pattern = re.compile('(\d+)-(\d+)')

    players = []

    # Fetch the roster page for each team and use BeautifulSoup to parse the HTML
    for team, roster_url in team_rosters.items():
        print('Getting {} players'.format(team.title()))

        r = requests.get(roster_url)
        if r.status_code != requests.codes.ok:
            raise RuntimeError(r.status_code, r.text)

        roster_page = BeautifulSoup(r.text, features='lxml')

        # Iterate through the active and injured reserve roster tables
        # skip the practice squad.
        for table in roster_page.find_all('table', summary='Roster'):
            squad = table.find('caption', class_='d3-o-table__caption')
            squad_name = squad.text.strip().lower()
            if squad_name.find('practice') < 0:
                for row in table.find_all('tr'):
                    fields = [team]
                    for col in row.find_all('td'):
                        col_val = col.text.strip()

                        height = pattern.match(col_val)
                        if height is not None:
                            # Convert height in feet & inches to just inches
                            inches = int(height.group(1)) * 12 + int(height.group(2))
                            fields.append(str(inches))
                        else:
                            fields.append(col_val)

                    if len(fields) > 1:
                        players.append(fields)

        # Be nice and take a short nap
        time.sleep(1)

    # Save to a CSV file
    fname = 'nfl-players-2018.csv'
    print('Saving {:d} players to {}'.format(len(players), fname))

    with open(fname, 'w') as pfile:
        writer = csv.writer(pfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, encoding='utf-8')

        writer.writerow(['team', 'name', 'number', 'position', 'height', 'weight', 'age', 'years', 'school'])
        for row in players:
            # Turn 'R' for 'Rookie' into 0 to match other years
            if row[-2] == 'R':
                row[-2] = 0

            writer.writerow(row)


if __name__ == '__main__':
    main()
