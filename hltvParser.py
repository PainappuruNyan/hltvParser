import requests
import time
import json
import random
import datetime
import pandas as pd
import csv
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.50"
}
all_links = []
match_stat = []


def get_data():
    for item in range(0, 1000, 100):
        url = f'https://www.hltv.org/results?offset={item}'
        r = requests.get(url=url, headers=headers)
        print(f'offset:{item}')
        with open(f'data/matches_{item}.html', 'w', encoding='utf-8') as file:
            file.write(r.text)


def get_links():
    for item in range(0, 101, 100):
        url = f'https://www.hltv.org/results?offset={item}'
        r = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        matches = soup.find_all('div', class_='results-sublist')
        for match in matches:
            links = match.find_all('a', class_='a-reset')
            for link in links:
                link = link.get('href')
                ml = f'https://www.hltv.org{link}'
                all_links.append(ml)
    count = 0
    for link in all_links[:1]:
        count += 1
        print(f'progress: {count}/ {len(all_links)}')
        req = requests.get(url=link, headers=headers)
        m = BeautifulSoup(req.text, 'lxml')
        stat_link = f"https://www.hltv.org{m.find('div', class_='results-center-stats').find('a', class_='results-stats').get('href')}"
        stat_pg = requests.get(url=stat_link, headers=headers)
        stat = BeautifulSoup(stat_pg.text, 'lxml')
        date = stat.find('div', class_='wide-grid').find('div', class_='small-text').find('span').text.split(' ')[0]
        match_date = datetime.strptime(date, "%Y-%m-%d")
        map_name1 = m.find('div', class_='flexbox-column').find_all('div', class_='mapholder')
        event_name = m.find('div', class_='event text-ellipsis').find('a').text
        match_type = \
            m.find('div', class_='standard-box veto-box').find('div', class_='padding preformatted-text').text.split(
                '*')[
                0].split('(')[0].strip().lower()
        if match_type == 'best of 3':
            match_type = 'bo3'
        elif match_type == 'best of 5':
            match_type = 'bo5'
        elif match_type == 'best of 1':
            match_type = 'bo1'
        print(match_type)
        for map_num, h in enumerate(map_name1):
            try:
                map_number = map_num + 1
                team2_last_map_win = 0
                team1_last_map_win = 0
                map_name = f"de_{h.find('div', class_='mapname').text.lower()}"
                team1_result = h.find('div', class_='results-left').find('div',
                                                                         class_='results-team-score').text.replace(
                    '-', '0')
                team2_result = h.find('span', class_='results-right').find('div',
                                                                           class_='results-team-score').text.replace(
                    '-', '0')
                head2head_team1_wins = m.find('div', class_='flexbox-column flexbox-center grow right-border').find(
                    'div',
                    class_='bold').text
                head2head_team2_wins = m.find('div', class_='flexbox-column flexbox-center grow left-border').find(
                    'div',
                    class_='bold').text
                team1 = m.find('div', class_='flexbox team1').find('a', class_='teamName').text.lower()
                team1_id = m.find('div', class_='flexbox team1').find('a', class_='teamName').get('href').split('/')[2]
                try:
                    team1_rank = m.find('div', class_='lineups').find_all('a', class_='a-reset')[0].text.split('#')[1]
                except IndexError:
                    team1_rank = "Unranked"

                team2 = m.find('div', class_='flexbox team2').find('a', class_='teamName').text.lower()
                team2_id = m.find('div', class_='flexbox team2').find('a', class_='teamName').get('href').split('/')[2]
                try:
                    team2_rank = m.find('div', class_='lineups').find_all('a', class_='a-reset')[1].text.split('#')[1]
                except IndexError:
                    team2_rank = "Unranked"
                match_id = link.split('/')[4]
                a = m.find_all('div', class_='lineup standard-box')[0]
                c = m.find_all('div', class_='lineup standard-box')[1]
                b = a.find('div', class_='players').find_all('td', class_='player')
                team1_players_id = []
                team1_players_name = []
                team2_players_id = []
                team2_players_name = []
                for player1 in b:
                    player1_id = player1.find('a').get('href').split('/')[2]
                    player1_name = player1.find('a').get('href').split('/')[3]
                    team1_players_name.append(player1_name)
                    team1_players_id.append(player1_id)

                d = c.find('div', class_='players').find_all('td', class_='player')
                for player2 in d:
                    player2_id = player2.find('a').get('href').split('/')[2]
                    player2_name = player2.find('a').get('href').split('/')[3]
                    team2_players_name.append(player2_name)
                    team2_players_id.append(player2_id)

                map_pick_team1 = 0
                map_pick_team2 = 0
                try:
                    picked1 = h.find('div', 'results played').find(class_='pick')
                    # picked2 = h.find('span', class_='result-right')
                    if picked1.find('div', class_='results-teamname text-ellipsis').text.lower() == team1:
                        map_pick_team1 = 1
                    else:
                        map_pick_team2 = 1
                except Exception as ex:
                    map_pick_team1 = 0
                    map_pick_team2 = 0
                print(map_pick_team1)
                print(map_pick_team2)

                team1_1month_stat_url = f'https://www.hltv.org/stats/teams/matches/{team1_id}/{team1}?startDate={(match_date - timedelta(days=30)).strftime("%Y-%m-%d")}&endDate={match_date.strftime("%Y-%m-%d")}&maps={map_name}'
                team2_1month_stat_url = f'https://www.hltv.org/stats/teams/matches/{team2_id}/{team2}?startDate={(match_date - timedelta(days=30)).strftime("%Y-%m-%d")}&endDate={match_date.strftime("%Y-%m-%d")}&maps={map_name}'
                team1_1month_stat_pg = requests.get(url=team1_1month_stat_url, headers=headers)
                team1_1month_stat = BeautifulSoup(team1_1month_stat_pg.text, 'lxml')
                try:
                    team1_map_played_in_month = 0
                    team1_map_wr_1month = 0
                    all_stat = team1_1month_stat.find('table', class_='stats-table').find('tbody').find_all('tr')
                    wins1 = 0
                    loses1 = 0
                    for stat in all_stat:
                        game_res = stat.find_all('td')[-1].text
                        if game_res == "L":
                            loses1 += 1
                        elif game_res == "W":
                            wins1 += 1

                        team1_map_played_in_month = wins1 + loses1

                        if wins1 or loses1 != 0:
                            team1_map_wr_1month = wins1 / (wins1 + loses1)
                        else:
                            team1_map_wr_1month = -1
                except Exception as ex:
                    print(f'1 {ex}')

                team2_1month_stat_pg = requests.get(url=team2_1month_stat_url, headers=headers)
                team2_1month_stat = BeautifulSoup(team2_1month_stat_pg.text, 'lxml')
                try:
                    team2_map_wr_1month = 0
                    team2_map_played_in_month = 0
                    all_stat = team2_1month_stat.find('table', class_='stats-table').find('tbody').find_all('tr')
                    wins2 = 0
                    loses2 = 0
                    for stat in all_stat:
                        game_res = stat.find_all('td')[-1].text
                        if game_res == "L":
                            loses2 += 1
                        elif game_res == "W":
                            wins2 += 1

                        team2_map_played_in_month = wins2 + loses2

                        if wins2 or loses2 != 0:
                            team2_map_wr_1month = wins1 / (wins1 + loses1)
                        else:
                            team2_map_wr_1month = -1
                except Exception as ex:

                    print(f'2 {ex}')

                team1_3month_stat_url = f'https://www.hltv.org/stats/teams/matches/{team1_id}/{team1}?startDate={(match_date - timedelta(days=90)).strftime("%Y-%m-%d")}&endDate={match_date.strftime("%Y-%m-%d")}&maps={map_name}'
                team2_3month_stat_url = f'https://www.hltv.org/stats/teams/matches/{team2_id}/{team2}?startDate={(match_date - timedelta(days=90)).strftime("%Y-%m-%d")}&endDate={match_date.strftime("%Y-%m-%d")}&maps={map_name}'

                team1_3month_stat_pg = requests.get(url=team1_3month_stat_url, headers=headers)
                team1_3month_stat = BeautifulSoup(team1_3month_stat_pg.text, 'lxml')
                try:
                    head2head_map_team1 = 0
                    team1_map_wr_3month = 0
                    team1_map_played_in_3month = 0
                    all_stat = team1_3month_stat.find('table', class_='stats-table').find('tbody').find_all('tr')
                    wins13 = 0
                    loses13 = 0
                    for stat in all_stat:
                        opponent = stat.find_all('td')[3].find('a').get('href').split('/')[3]
                        last_match_date1 = stat.find_all('td')[0].text.replace('/', '-')
                        last_match_date = datetime.strptime(last_match_date1, "%d-%m-%y").strftime("%Y-%m-%d %H:%M:%S")
                        game_res = stat.find_all('td')[-1].text
                        if game_res == "L":
                            loses13 += 1
                        elif game_res == 'W':
                            wins13 += 1

                        team1_map_played_in_3month = wins13 + loses13
                        if opponent == team2_id and game_res == 'W' and last_match_date != str(match_date):
                            print(match_date, last_match_date)
                            print(opponent, team2_id, game_res)
                            team1_last_map_win = 1
                            head2head_map_team1 += 1

                        if wins13 or loses13 != 0:
                            team1_map_wr_3month = wins13 / (wins13 + loses13)
                        else:
                            team1_map_wr_3month = -1
                except Exception as ex:
                    print(f'3 {ex}')

                team2_3month_stat_pg = requests.get(url=team2_3month_stat_url, headers=headers)
                team2_3month_stat = BeautifulSoup(team2_3month_stat_pg.text, 'lxml')
                try:
                    head2head_map_team2 = 0
                    team2_map_wr_3month = 0
                    team2_map_played_in_3month = 0
                    all_stat = team2_3month_stat.find('table', class_='stats-table').find('tbody').find_all('tr')
                    wins23 = 0
                    loses23 = 0
                    for stat in all_stat:
                        last_match_date1 = stat.find_all('td')[0].text.replace('/', '-')
                        last_match_date = datetime.strptime(last_match_date1, "%d-%m-%y").strftime("%Y-%m-%d %H:%M:%S")
                        opponent = stat.find_all('td')[3].find('a').get('href').split('/')[3]
                        game_res = stat.find_all('td')[-1].text
                        if game_res == "L":
                            loses23 += 1
                        elif game_res == "W":
                            wins23 += 1

                        team2_map_played_in_3month = wins23 + loses23
                        if opponent == team1_id and game_res == 'W' and last_match_date != str(match_date):
                            print(type(match_date), type(last_match_date))
                            print(match_date, last_match_date)
                            print(opponent, team1_id, game_res)
                            team2_last_map_win = 1
                            head2head_map_team2 += 1

                        if wins23 or loses23 != 0:
                            team2_map_wr_1month = wins23 / (wins23 + loses23)
                        else:
                            team2_map_wr_3month = -1
                except Exception as ex:
                    print(f'4 {ex}')

                if int(team1_result) < int(team2_result):
                    map_result = team2
                else:
                    map_result = team1

                if team1_result == '0' and team2_result == '0':
                    continue

                match_stat.append(
                    {
                        'map': map_name,
                        'map number': map_number,
                        'match type': match_type,
                        'match date': match_date.strftime("%Y-%m-%d"),
                        'match id': match_id,
                        'event name': event_name,
                        'head2head results': f'{head2head_team1_wins} : {head2head_team2_wins}',
                        'head2head_map': f'{head2head_map_team1} : {head2head_map_team2}',
                        'team 1 players id': team1_players_id[:5],
                        'team 2 players id': team2_players_id[:5],
                        'team 1 players name': team1_players_name[:5],
                        'team 2 players name': team2_players_name[:5],
                        'map pick team 1': map_pick_team1,
                        'map pick team 2': map_pick_team2,

                        'team 1': team1,
                        'team 1 id': team1_id,
                        'team 1 rank': team1_rank,
                        'team 1 result': team1_result,
                        'team 1 wins 1 month': wins1,
                        'team 1 loses 1 month': loses1,
                        'team 1 wins 3 month': wins13,
                        'team 1 loses 3 month': loses13,
                        'team 1 wr 1 month': team1_map_wr_1month,
                        'team 1 wr 3 month': team1_map_wr_3month,
                        'team 1 map played in 1 month': team1_map_played_in_month,
                        'team 1 map played in 3 month': team1_map_played_in_3month,
                        'team 1 last map win': team1_last_map_win,

                        'team 2': team2,
                        'team 2 id': team2_id,
                        'team 2 rank': team2_rank,
                        'team 2 result': team2_result,
                        'team 2 wins 1 month': wins2,
                        'team 2 loses 1 month': loses2,
                        'team 2 wins 3 month': wins23,
                        'team 2 loses 3 month': loses23,
                        'team 2 wr 1 month': team2_map_wr_1month,
                        'team 2 wr 3 month': team2_map_wr_3month,
                        'team 2 map played in 1 month': team2_map_played_in_month,
                        'team 2 map played in 3 month': team2_map_played_in_3month,
                        'team 2 last map win': team2_last_map_win,

                        'map winner': map_result
                    }
                )
                with open('data/hltvData.csv', mode='a') as csv_file:
                    csv_file.write(match_stat)

                time.sleep(random.randrange(2, 4))
            except Exception as ex:
                error = ex
                with open('log.csv', 'a', encoding='utf-8') as file:
                    file.write(link)
                    file.write(str(error))
        time.sleep(random.randrange(2, 4))

    # with open("projects_data.json", "a", encoding="utf-8") as file:
    #     json.dump(match_stat, file, indent=4, ensure_ascii=False)


def main():
    get_links()


if __name__ == '__main__':
    main()