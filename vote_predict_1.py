import datetime
from datetime import datetime, timedelta
from collections import Counter
import catboost
import pandas as pd
import requests
from bs4 import BeautifulSoup

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.50"
}
all_links = []


def get_predict():
    link = input("link pls ")
    req = requests.get(url=link, headers=headers)
    m = BeautifulSoup(req.text, "lxml")
    match_date = datetime.today().date()
    map_name1 = m.find("div", class_="flexbox-column").find_all("div", class_="mapholder")
    event_name = m.find("div", class_="event text-ellipsis").find("a").text
    match_type = (
        m.find("div", class_="standard-box veto-box")
            .find("div", class_="padding preformatted-text")
            .text.split("*")[0]
            .split("(")[0]
            .strip()
            .lower()
    )
    if match_type == "best of 3":
        match_type = "bo3"
    elif match_type == "best of 5":
        match_type = "bo5"
    elif match_type == "best of 1":
        match_type = "bo1"
    for map_num, h in enumerate(map_name1):
        map_number = map_num + 1
        team2_last_map_win = 0
        team1_last_map_win = 0
        map_name = f"de_{h.find('div', class_='mapname').text.lower()}"
        head2head_team1_wins = (
            m.find("div", class_="flexbox-column flexbox-center grow right-border").find("div", class_="bold").text
        )
        head2head_team2_wins = (
            m.find("div", class_="flexbox-column flexbox-center grow left-border").find("div", class_="bold").text
        )
        team1 = m.find("div", class_="flexbox team1").find("a", class_="teamName").text.lower()
        team1_id = m.find("div", class_="flexbox team1").find("a", class_="teamName").get("href").split("/")[2]
        try:
            team1_rank = m.find("div", class_="lineups").find_all("a", class_="a-reset")[0].text.split("#")[1]
        except IndexError:
            team1_rank = "Unranked"

        team2 = m.find("div", class_="flexbox team2").find("a", class_="teamName").text.lower()
        team2_id = m.find("div", class_="flexbox team2").find("a", class_="teamName").get("href").split("/")[2]
        try:
            team2_rank = m.find("div", class_="lineups").find_all("a", class_="a-reset")[1].text.split("#")[1]
        except IndexError:
            team2_rank = "Unranked"
        match_id = link.split("/")[4]
        a = m.find_all("div", class_="lineup standard-box")[0]
        c = m.find_all("div", class_="lineup standard-box")[1]
        b = a.find("div", class_="players").find_all("td", class_="player")
        team1_players_name = []
        team2_players_name = []
        for player1 in b[5:10]:
            player1_name = player1.find("div", {"class": "text-ellipsis"}).text
            team1_players_name.append(player1_name)

        d = c.find("div", class_="players").find_all("td", class_="player")
        for player2 in d[5:10]:
            player2_name = player2.find("div", {"class": "text-ellipsis"}).text
            team2_players_name.append(player2_name)

        map_pick_team1 = 0
        map_pick_team2 = 0
        try:
            picked1 = h.find("div", "results played").find(class_="pick")
            if picked1.find("div", class_="results-teamname text-ellipsis").text.lower() == team1:
                map_pick_team1 = 1
            else:
                map_pick_team2 = 1
        except Exception as ex:
            map_pick_team1 = 0
            map_pick_team2 = 0
        match_date_minus_1_day = match_date - timedelta(days=1)
        team1_1month_stat_url = f'https://www.hltv.org/stats/teams/matches/{team1_id}/{team1}?startDate={(match_date_minus_1_day - timedelta(days=30)).strftime("%Y-%m-%d")}&endDate={match_date_minus_1_day.strftime("%Y-%m-%d")}&maps={map_name}'
        team2_1month_stat_url = f'https://www.hltv.org/stats/teams/matches/{team2_id}/{team2}?startDate={(match_date_minus_1_day - timedelta(days=30)).strftime("%Y-%m-%d")}&endDate={match_date_minus_1_day.strftime("%Y-%m-%d")}&maps={map_name}'
        team1_1month_stat_pg = requests.get(url=team1_1month_stat_url, headers=headers)
        team1_1month_stat = BeautifulSoup(team1_1month_stat_pg.text, "lxml")
        try:
            team1_map_played_in_month = 0
            team1_map_wr_1month = 0
            all_stat = team1_1month_stat.find("table", class_="stats-table").find("tbody").find_all("tr")
            wins1 = 0
            loses1 = 0
            for stat in all_stat:
                game_res = stat.find_all("td")[-1].text
                if game_res == "L":
                    loses1 += 1
                elif game_res == "W":
                    wins1 += 1

                team1_map_played_in_month = wins1 + loses1

                if (wins1 + loses1) != 0:
                    team1_map_wr_1month = wins1 / (wins1 + loses1)
                else:
                    team1_map_wr_1month = -1
        except Exception as ex:
            print(f"1 {ex}")

        team2_1month_stat_pg = requests.get(url=team2_1month_stat_url, headers=headers)
        team2_1month_stat = BeautifulSoup(team2_1month_stat_pg.text, "lxml")
        try:
            team2_map_wr_1month = 0
            team2_map_played_in_month = 0
            all_stat = team2_1month_stat.find("table", class_="stats-table").find("tbody").find_all("tr")
            wins2 = 0
            loses2 = 0
            for stat in all_stat:
                game_res = stat.find_all("td")[-1].text
                if game_res == "L":
                    loses2 += 1
                elif game_res == "W":
                    wins2 += 1

                team2_map_played_in_month = wins2 + loses2

                if (wins2 + loses2) != 0:
                    team2_map_wr_1month = wins2 / (wins2 + loses2)
                else:
                    team2_map_wr_1month = -1
        except Exception as ex:

            print(f"2 {ex}")

        team1_3month_stat_url = f'https://www.hltv.org/stats/teams/matches/{team1_id}/{team1}?startDate={(match_date_minus_1_day - timedelta(days=90)).strftime("%Y-%m-%d")}&endDate={match_date_minus_1_day.strftime("%Y-%m-%d")}&maps={map_name}'
        team2_3month_stat_url = f'https://www.hltv.org/stats/teams/matches/{team2_id}/{team2}?startDate={(match_date_minus_1_day - timedelta(days=90)).strftime("%Y-%m-%d")}&endDate={match_date_minus_1_day.strftime("%Y-%m-%d")}&maps={map_name}'

        team1_3month_stat_pg = requests.get(url=team1_3month_stat_url, headers=headers)
        team1_3month_stat = BeautifulSoup(team1_3month_stat_pg.text, "lxml")
        try:
            head2head_map_team1 = 0
            team1_map_wr_3month = 0
            team1_map_played_in_3month = 0
            all_stat = team1_3month_stat.find("table", class_="stats-table").find("tbody").find_all("tr")
            wins13 = 0
            loses13 = 0
            for stat in all_stat:
                opponent = stat.find_all("td")[3].find("a").get("href").split("/")[3]
                last_match_date1 = stat.find_all("td")[0].text.replace("/", "-")
                last_match_date = datetime.strptime(last_match_date1, "%d-%m-%y").strftime("%Y-%m-%d %H:%M:%S")
                game_res = stat.find_all("td")[-1].text
                if game_res == "L":
                    loses13 += 1
                elif game_res == "W":
                    wins13 += 1

                team1_map_played_in_3month = wins13 + loses13
                if opponent == team2_id and game_res == "W" and last_match_date != str(match_date):
                    team1_last_map_win = 1
                    head2head_map_team1 += 1

                if (wins13 + loses13) != 0:
                    team1_map_wr_3month = wins13 / (wins13 + loses13)
                else:
                    team1_map_wr_3month = -1
        except Exception as ex:
            print(f"3 {ex}")

        team2_3month_stat_pg = requests.get(url=team2_3month_stat_url, headers=headers)
        team2_3month_stat = BeautifulSoup(team2_3month_stat_pg.text, "lxml")
        try:
            head2head_map_team2 = 0
            team2_map_wr_3month = 0
            team2_map_played_in_3month = 0
            all_stat = team2_3month_stat.find("table", class_="stats-table").find("tbody").find_all("tr")
            wins23 = 0
            loses23 = 0
            for stat in all_stat:
                last_match_date1 = stat.find_all("td")[0].text.replace("/", "-")
                last_match_date = datetime.strptime(last_match_date1, "%d-%m-%y").strftime("%Y-%m-%d %H:%M:%S")
                opponent = stat.find_all("td")[3].find("a").get("href").split("/")[3]
                game_res = stat.find_all("td")[-1].text
                if game_res == "L":
                    loses23 += 1
                elif game_res == "W":
                    wins23 += 1

                team2_map_played_in_3month = wins23 + loses23
                if opponent == team1_id and game_res == "W" and last_match_date != str(match_date):
                    team2_last_map_win = 1
                    head2head_map_team2 += 1

                if (wins23 + loses23) != 0:
                    team2_map_wr_1month = wins23 / (wins23 + loses23)
                else:
                    team2_map_wr_3month = -1
        except Exception as ex:
            print(f"4 {ex}")

        ###

        df = pd.DataFrame(
            data={
                "match_date": match_date.isoformat(),
                "match_id": match_id,
                "match_type": match_type,
                "event_name": event_name,
                "map_number": map_number,
                "map": map_name,
                "map_pick_team_1": map_pick_team1,
                "map_pick_team_2": map_pick_team2,
                "team1": team1,
                "team2": team2,
                "team1_rank": team1_rank,
                "team2_rank": team2_rank,
                "head2head_team1_wins": head2head_team1_wins,
                "head2head_team2_wins": head2head_team2_wins,
                "head2head_map_team1": head2head_map_team1,
                "head2head_map_team2": head2head_map_team2,
                "team_1_players_name": " ".join(team1_players_name[:5]),
                "team_2_players_name": " ".join(team2_players_name[:5]),
                "team1_wins_1_month": wins1,
                "team2_wins_1_month": wins2,
                "team1_loses_1_month": loses1,
                "team2_loses_1_month": loses2,
                "team1_wins_3_month": wins13,
                "team2_wins_3_month": wins23,
                "team1_loses_3_month": loses13,
                "team2_loses_3_month": loses23,
                "team1_wr_1_month": team1_map_wr_1month,
                "team2_wr_1_month": team2_map_wr_1month,
                "team1_wr_3_month": team1_map_wr_3month,
                "team2_wr_3_month": team2_map_wr_3month,
                "team1_map_played_in_1_month": team1_map_played_in_month,
                "team2_map_played_in_1_month": team2_map_played_in_month,
                "team1_map_played_in_3_month": team1_map_played_in_3month,
                "team2_map_played_in_3_month": team2_map_played_in_3month,
                "team1_last_map_win": team1_last_map_win,
                "team2_last_map_win": team2_last_map_win,
            },
            index=[0],
        )
        df.columns = [item.replace(" ", "") for item in list(df.columns)]
        df = df.rename({"team_2": "team2", "team_2_id": "team2_id"}, axis=1)
        df = df.rename({"_team_2": "team2", "team_2_id": "team2_id"}, axis=1)
        df = df.drop_duplicates()
        df = df.dropna()
        df["map_number"] = df["map_number"].astype("int")
        df["head2head_map_team1"] = df["head2head_map_team1"].astype("int")
        df["head2head_map_team2"] = df["head2head_map_team2"].astype("int")
        df["map_pick_team_1"] = df["map_pick_team_1"].astype("int")
        df["map_pick_team_2"] = df["map_pick_team_2"].astype("int")
        df["head2head_team1_wins"] = df["head2head_team1_wins"].astype("int")
        df["head2head_team2_wins"] = df["head2head_team2_wins"].astype("int")
        df["team1_map_played_in_3_month"] = df["team1_map_played_in_3_month"].astype("int")
        df["team2_map_played_in_3_month"] = df["team2_map_played_in_3_month"].astype("int")
        df["rank_difference"] = df["team1_rank"].astype("int") - df["team2_rank"].astype("int")
        df["head2head_teams_wins_diff"] = df["head2head_team1_wins"] - df["head2head_team2_wins"]
        df["head2head_map_teams_diff"] = df["head2head_map_team1"] - df["head2head_map_team2"]
        df["team_last_map_win_diff"] = df["team1_last_map_win"] - df["team2_last_map_win"]
        df["team_wins_diff"] = df["team1_wins_1_month"] - df["team2_wins_1_month"]
        df["team_loses_diff"] = df["team1_loses_1_month"] - df["team2_loses_1_month"]
        df["team_wins_diff"] = df["team1_wins_1_month"] - df["team2_wins_1_month"]
        df["team_loses_diff"] = df["team1_loses_1_month"] - df["team2_loses_1_month"]
        df["team_wins_3month_diff"] = df["team1_wins_3_month"] - df["team2_wins_3_month"]
        df["team_loses_3month_diff"] = df["team1_loses_3_month"] - df["team2_loses_3_month"]
        df["maps_played_diff"] = df["team1_map_played_in_1_month"] - df["team2_map_played_in_1_month"]
        df["maps_played_3month_diff"] = df["team1_map_played_in_3_month"] - df["team2_map_played_in_3_month"]
        df["wr_diff"] = df["team1_wr_1_month"] - df["team2_wr_1_month"]
        df["wr_3month_diff"] = df["team1_wr_3_month"] - df["team2_wr_3_month"]
        df = df[
            [
                "match_date",
                "wr_3month_diff",
                "wr_diff",
                "maps_played_3month_diff",
                "maps_played_diff",
                "team_loses_3month_diff",
                "team_wins_3month_diff",
                "team_loses_diff",
                "head2head_teams_wins_diff",
                "team_last_map_win_diff",
                "team_wins_diff",
                "head2head_map_teams_diff",
                "match_id",
                "map_number",
                "map",
                "map_pick_team_1",
                "map_pick_team_2",
                "rank_difference",
                "head2head_team1_wins",
                "head2head_team2_wins",
                "head2head_map_team1",
                "head2head_map_team2",
                "team1_wins_1_month",
                "team2_wins_1_month",
                "team1_loses_1_month",
                "team2_loses_1_month",
                "team1_wins_3_month",
                "team2_wins_3_month",
                "team1_loses_3_month",
                "team2_loses_3_month",
                "team1_wr_1_month",
                "team2_wr_1_month",
                "team1_wr_3_month",
                "team2_wr_3_month",
                "team1_map_played_in_1_month",
                "team2_map_played_in_1_month",
                "team1_map_played_in_3_month",
                "team2_map_played_in_3_month",
                "team1_last_map_win",
                "team2_last_map_win",
            ]
        ]
        df = df.drop(
            [
                "match_id",
                "map_number",
                "match_date",
            ],
            axis=1,
        )

        model1 = catboost.CatBoostClassifier()
        model1.load_model("total_66_grid_search")

        model2 = catboost.CatBoostClassifier()
        model2.load_model("total_auc")

        model3 = catboost.CatBoostClassifier()
        model3.load_model("total_recall_0_1_v2")

        print(map_name)

        predicts = [model1.predict(df)[0], model2.predict(df)[0],  0 if model3.predict(df)[0] == 1 else 1]
        print(f"Will total 26.5: {'yes' if Counter(predicts).most_common()[0][0] == 1 else 'no'}")


def main():
    get_predict()


if __name__ == "__main__":
    main()
