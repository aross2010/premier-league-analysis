# used to scrape match data from fbref.com
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import csv
import pandas as pd
import os
import traceback


matches_df = pd.read_csv('fixture.csv')
players_df = pd.read_csv('player.csv')
club_members_df = pd.read_csv('club_member.csv')

def matches(driver):
    driver.get('https://fbref.com/en/comps/9/2023-2024/schedule/2023-2024-Premier-League-Scores-and-Fixtures')

    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # table with all matches
    match_table = soup.find('table', class_='stats_table')
    matches = match_table.find_all('tr', {'data-row': True, 'class': None})

    with open('match.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['match_id', 'date', 'home_club', 'away_club']
    
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    
        for id, match in enumerate(matches):
            match_id = id + 1
            date = match.find('td', {'data-stat': 'date'}).text.strip()
            home_club = match.find('td', {'data-stat': 'home_team'}).text.strip()
            away_club = match.find('td', {'data-stat': 'away_team'}).text.strip()
        
            match_data = {
                'match_id': match_id,
                'date': date,
                'home_club': home_club,
                'away_club': away_club,
            }
        
            writer.writerow(match_data)


    driver.quit()

def match_stats(driver):

    driver.get('https://fbref.com/en/comps/9/2023-2024/schedule/2023-2024-Premier-League-Scores-and-Fixtures')

    print("Waiting for page to load...")

    time.sleep(10)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    match_table = soup.find('table', class_='stats_table')
    match_reports = match_table.find_all('a', string='Match Report')

    # extract the a href link from each match report
    matches = [f'https://fbref.com{report['href']}' for report in match_reports]

    time.sleep(10)
    
    for id, match in enumerate(matches):
        print(f"Scraping match {id + 1} of {len(matches)}")
        driver.get(match)
        print("Waiting for match report to load...")
        time.sleep(10)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        get_player_stats(id+1, soup)
        get_club_stats(id+1, soup)
        print(f"Finished scraping match {id + 1} of {len(matches)}")

def get_club_stats(match_id, soup):
    home_club = matches_df.loc[matches_df['match_id'] == match_id, 'home_club'].values[0]
    away_club = matches_df.loc[matches_df['match_id'] == match_id, 'away_club'].values[0]

    goals_scored = soup.find('div', class_='scorebox').find_all('div', class_='score')
    home_goals = goals_scored[0].text.strip()
    away_goals = goals_scored[1].text.strip()

    team_stats_container = soup.find('div', id='team_stats')

    # find the tr that has text Possession, then get the very next tr and find all the strong tags
    possession_row = team_stats_container.find('tr', string=lambda x: x and 'Possession' in x)
    possession_row = possession_row.find_next('tr')
    possessions = possession_row.find_all('strong')
    possessions = [possession.text.strip('%') for possession in possessions]
    home_possession = possessions[0]
    away_possession = possessions[1]

    club_stats = [
        {
            'match_id': match_id,
            'club': home_club,
            'goals_scored': home_goals,
            'possession': home_possession,
        },
        {
            'match_id': match_id,
            'club': away_club,
            'goals_scored': away_goals,
            'possession': away_possession,
        }
    ]

    if os.path.exists('club_stat.csv'):
        try:
            df = pd.read_csv('club_stat.csv')
            if not df.empty:
                club_stat_id_counter = df['club_stat_id'].max() + 1
            else:
                club_stat_id_counter = 1
        except pd.errors.EmptyDataError:
            club_stat_id_counter = 1
    else:
        club_stat_id_counter = 1

    file_exists = os.path.exists('club_stat.csv')
    with open('club_stat.csv', 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['club_stat_id', 'match_id', 'club', 'goals_scored', 'possession']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists or (file_exists and os.stat('club.csv').st_size == 0):
            writer.writeheader()
        for club in club_stats:
            df = pd.read_csv('club.csv')
            club['club_stat_id'] = club_stat_id_counter
            writer.writerow(club)
            club_stat_id_counter += 1

def get_player_stats(match_id, soup):

    # get home an away club names from match_id in matches_df
    home_club = matches_df.loc[matches_df['match_id'] == match_id, 'home_club'].values[0]
    away_club = matches_df.loc[matches_df['match_id'] == match_id, 'away_club'].values[0]

    # set up players and their IDs for those who played 
    home_squad = soup.find('div', class_='lineup', id='a').find_all('tr')
    away_squad = soup.find('div', class_='lineup', id='b').find_all('tr')

    home_players = parse_squad(home_squad, home_club, match_id)
    away_players = parse_squad(away_squad, away_club, match_id)

    # players who played are now set up, fetch individual stats
    
    # stat summary tables - id contains the word 'summary'
    stat_summary_tables = soup.find_all('table', class_='stats_table', id=lambda x: x and 'summary' in x)
    pass_types_tables = soup.find_all('table', class_='stats_table', id=lambda x: x and 'passing_types' in x)
    defensive_tables = soup.find_all('table', class_='stats_table', id=lambda x: x and 'defense' in x)
    misc_tables = soup.find_all('table', class_='stats_table', id=lambda x: x and 'misc' in x)
    keeper_tables = soup.find_all('table', class_='stats_table', id=lambda x: x and 'keeper' in x)
    shots_tables_container = soup.find('div', id='all_shots')
    # all tables where id != 'shots_all
    shots_tables = shots_tables_container.find_all('table', class_='stats_table', id=lambda x: x and 'shots' in x and 'all' not in x)



    # get player stats first
    for i, table in enumerate(stat_summary_tables):
        table = table.find('tbody')
        rows = table.find_all('tr', {'data-row': True, 'class': None})
        for row in rows:
            player_name = row.find('th', {'data-stat': 'player'}).text.strip()
            target_players = home_players if i == 0 else away_players
            
            if player_name not in target_players:
                print(f"Player {player_name} not found in {home_club if i == 0 else away_club}")
                continue
            target_players[player_name].update({
                'minutes': row.find('td', {'data-stat': 'minutes'}).text.strip(),
                'goals': row.find('td', {'data-stat': 'goals'}).text.strip(),
                'assists': row.find('td', {'data-stat': 'assists'}).text.strip(),
                'pens_made': row.find('td', {'data-stat': 'pens_made'}).text.strip(),
                'pens_attempted': row.find('td', {'data-stat': 'pens_att'}).text.strip(),
                'shots_attempted': row.find('td', {'data-stat': 'shots'}).text.strip(),
                'shots_on_target': row.find('td', {'data-stat': 'shots_on_target'}).text.strip(),
                'yellow_cards': row.find('td', {'data-stat': 'cards_yellow'}).text.strip(),
                'red_cards': row.find('td', {'data-stat': 'cards_red'}).text.strip(),
                'touches': row.find('td', {'data-stat': 'touches'}).text.strip(),
                'tackles': row.find('td', {'data-stat': 'tackles'}).text.strip(),
                'interceptions': row.find('td', {'data-stat': 'interceptions'}).text.strip(),
                'blocks': row.find('td', {'data-stat': 'blocks'}).text.strip(),
                'xg': row.find('td', {'data-stat': 'xg'}).text.strip(),
                'xa': row.find('td', {'data-stat': 'xg_assist'}).text.strip(),
                'shot_creating_actions': row.find('td', {'data-stat': 'sca'}).text.strip(),
                'goal_creating_actions': row.find('td', {'data-stat': 'gca'}).text.strip(),
                'passes_attempted': row.find('td', {'data-stat': 'passes'}).text.strip(),
                'passes_completed': row.find('td', {'data-stat': 'passes_completed'}).text.strip(),
                'dribbles_attempted': row.find('td', {'data-stat': 'take_ons'}).text.strip(),
                'dribbles_completed': row.find('td', {'data-stat': 'take_ons_won'}).text.strip(),
            })

    for i, table in enumerate(pass_types_tables):
        table = table.find('tbody')
        rows = table.find_all('tr', {'data-row': True, 'class': None})
        for row in rows:
            player_name = row.find('th', {'data-stat': 'player'}).text.strip()
            target_players = home_players if i == 0 else away_players
            
            if player_name not in target_players:
                print(f"Player {player_name} not found in {home_club if i == 0 else away_club}")
                continue
            target_players[player_name].update({
                'crosses': row.find('td', {'data-stat': 'crosses'}).text.strip(),
                'throw_ins': row.find('td', {'data-stat': 'throw_ins'}).text.strip(),
                'corner_kicks': row.find('td', {'data-stat': 'corner_kicks'}).text.strip(),
            })
    
    for i, table in enumerate(defensive_tables):
        table = table.find('tbody')
        rows = table.find_all('tr', {'data-row': True, 'class': None})
        for row in rows:
            player_name = row.find('th', {'data-stat': 'player'}).text.strip()
            target_players = home_players if i == 0 else away_players
            
            if player_name not in target_players:
                print(f"Player {player_name} not found in {home_club if i == 0 else away_club}")
                continue
            target_players[player_name].update({
                'shots_blocked': row.find('td', {'data-stat': 'blocked_shots'}).text.strip(),
                'passes_blocked': row.find('td', {'data-stat': 'blocked_passes'}).text.strip(),
                'clearances': row.find('td', {'data-stat': 'clearances'}).text.strip(),
            })
    
    for i, table in enumerate(misc_tables):
        table = table.find('tbody')
        rows = table.find_all('tr', {'data-row': True, 'class': None})
        for row in rows:
            player_name = row.find('th', {'data-stat': 'player'}).text.strip()
            target_players = home_players if i == 0 else away_players
            
            if player_name not in target_players:
                print(f"Player {player_name} not found in {home_club if i == 0 else away_club}")
                continue
            target_players[player_name].update({
                'fouls_committed': row.find('td', {'data-stat': 'fouls'}).text.strip(),
                'fouls_drawn': row.find('td', {'data-stat': 'fouled'}).text.strip(),
                'offsides': row.find('td', {'data-stat': 'offsides'}).text.strip(),
                'pens_won': row.find('td', {'data-stat': 'pens_won'}).text.strip(),
                'pens_conceded': row.find('td', {'data-stat': 'pens_conceded'}).text.strip(),
                'own_goals': row.find('td', {'data-stat': 'own_goals'}).text.strip(),
                'recoveries': row.find('td', {'data-stat': 'ball_recoveries'}).text.strip(),
                'aeriel_duels_won': row.find('td', {'data-stat': 'aerials_won'}).text.strip(),
                'aeriel_duels_lost': row.find('td', {'data-stat': 'aerials_lost'}).text.strip(),
            })

    for i, table in enumerate(keeper_tables):
        table = table.find('tbody')
        rows = table.find_all('tr', {'data-row': True, 'class': None})
        for row in rows:
            player_name = row.find('th', {'data-stat': 'player'}).text.strip()
            target_players = home_players if i == 0 else away_players
            
            if player_name not in target_players:
                print(f"Player {player_name} not found in {home_club if i == 0 else away_club}")
                continue
            target_players[player_name].update({
                'sot_against': row.find('td', {'data-stat': 'gk_shots_on_target_against'}).text.strip(),
                'goals_against': row.find('td', {'data-stat': 'gk_goals_against'}).text.strip(),
                'saves': row.find('td', {'data-stat': 'gk_saves'}).text.strip(),
                'psxg_against': row.find('td', {'data-stat': 'gk_psxg'}).text.strip(),
            })

    if os.path.exists('player_stat.csv'):
        try:
            df = pd.read_csv('player_stat.csv')
            if not df.empty:
                stat_id_counter = df['stat_id'].max() + 1
            else:
                stat_id_counter = 1
        except pd.errors.EmptyDataError:
            stat_id_counter = 1
    else:
        stat_id_counter = 1
    
    file_exists = os.path.exists('player_stat.csv')
    with open('player_stat.csv', 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['stat_id', 'match_id', 'member_id', 'minutes', 'goals', 'assists', 'pens_made', 'pens_attempted',
                      'shots_attempted', 'shots_on_target', 'yellow_cards', 'red_cards', 'touches',
                      'tackles', 'interceptions', 'blocks', 'xg', 'xa', 'passes_attempted',
                      'passes_completed', 'dribbles_attempted', 'dribbles_completed',
                      'crosses', 'throw_ins', 'corner_kicks',
                      'shots_blocked', 'passes_blocked', 'clearances',
                      'fouls_committed', 'fouls_drawn', 'offsides',
                      'pens_won', 'pens_conceded', 'own_goals', 'shot_creating_actions', 'goal_creating_actions',
                      'recoveries', 'aeriel_duels_won', 'aeriel_duels_lost',
                      'sot_against', 'goals_against', 
                      'saves','psxg_against', 'subbed_in', 'subbed_off', 'started']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists or (file_exists and os.stat('player_stat.csv').st_size == 0):
            writer.writeheader()

        for player in list(home_players.values()) + list(away_players.values()):
            player['stat_id'] = stat_id_counter
            stat_id_counter += 1
            clean_row = {field: player.get(field, 'NULL') for field in fieldnames}
            writer.writerow(clean_row)

    goals = []

    # get stats for goal table
    for i, table in enumerate(shots_tables):
        table = table.find('tbody')
        rows = table.find_all('tr', {'data-row': True})
        for row in rows:
            outcome = row.find('td', {'data-stat': 'outcome'}).text.strip()
            if outcome != 'Goal':
                continue
            player_name = row.find('td', {'data-stat': 'player'}).text.strip() 
            # remove the (pen) from the player name
            player_name = player_name.split(' (')[0]
            target_players = home_players if i == 0 else away_players

            if player_name not in target_players:
                print(f"Player {player_name} not found in shots table")
                continue

            method = 'Open Play'
            if '(pen)' in player_name: method = 'Penalty'
            notes_box = row.find('td', {'data-stat': 'notes'})
            if notes_box.text:
                if notes_box.text.strip() == 'Free Kick':
                    method = notes_box.text.strip()

            assist_player = None
            sca_player = row.find('td', {'data-stat': 'sca_1_player'}) 
            if sca_player:
                sca_player = sca_player.text.strip()
                sca = row.find('td', {'data-stat': 'sca_1_type'})
                if sca:
                    sca = sca.text.strip()
                    if 'Pass' in sca:
                        assist_player = sca_player
            minute = row.find('th', {'data-stat': 'minute'}).text.strip()
            if '+' in minute:
                base, extra = minute.split('+')
                minute = int(base) + int(extra)
                if base == '45':
                    half = 1
                elif base == '90':
                    half = 2
                else:
                    half = 1 if int(base) <= 45 else 2
            else:
                minute = int(minute)
                half = 1 if minute <= 45 else 2

            goal = {
                'minute': minute,
                'half': half,
                'xg': row.find('td', {'data-stat': 'xg_shot'}).text.strip(),
                'psxg': row.find('td', {'data-stat': 'psxg_shot'}).text.strip(),
                'yards_out': row.find('td', {'data-stat': 'distance'}).text.strip(),
                'body_part': row.find('td', {'data-stat': 'body_part'}).text.strip(),
                'method': method, 
                'match_id': match_id,
                'scorer_id': target_players[player_name]['member_id'],
                'club': home_club if i == 0 else away_club
            }
            if assist_player:
                goal['assist_id'] = target_players[assist_player]['member_id']
            goals.append(goal)

    if os.path.exists('goal.csv'):
        try:
            df = pd.read_csv('goal.csv')
            if not df.empty:
                goal_id_counter = df['goal_id'].max() + 1
            else:
                goal_id_counter = 1
        except pd.errors.EmptyDataError:
            goal_id_counter = 1
    else:
        goal_id_counter = 1
    
    file_exists = os.path.exists('goal.csv')
    with open('goal.csv', 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['goal_id', 'minute', 'half', 'xg', 'psxg', 'yards_out', 'body_part', 'method', 'match_id', 'scorer_id', 'assist_id', 'club']
    
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists or (file_exists and os.stat('goal.csv').st_size == 0):
            writer.writeheader()
        for goal in goals:
            goal['goal_id'] = goal_id_counter
            clean_row = {field: goal.get(field, 'NULL') for field in fieldnames}
            writer.writerow(clean_row)
            goal_id_counter += 1

def parse_squad(squad_rows, club_name, match_id):
    players = {}
    starters = True

    for row in squad_rows:
        row_breaker = row.find('th')
        if row_breaker:
            if row_breaker.text.strip() == 'Bench':
                starters = False
            continue
        player = row.find('a')
        player_name = player.text.strip()
        member = club_members_df[(club_members_df['name'] == player_name) & (club_members_df['club'] == club_name)]
        if member.empty: 
            continue
        member_id = member.iloc[0]['member_id']
        sub_icon = row.find('div', class_='substitute_in')
        started = 'TRUE' if starters else 'FALSE'
        subbed_off = 'TRUE' if sub_icon and starters else 'FALSE'
        subbed_in = 'TRUE' if sub_icon and not starters else 'FALSE'
        # dont include players who did not play
        if subbed_in == 'FALSE' and started == 'FALSE':
            continue
        players[player_name] = {
            'match_id': match_id,
            'member_id': member_id,
            'started': started,
            'subbed_in': subbed_in,
            'subbed_off': subbed_off
        }

    
    return players

def main():

    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    try:
        # matches(driver)
        match_stats(driver)
    except Exception as e:
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    main()