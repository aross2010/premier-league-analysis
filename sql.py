import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',      
    password='root',  
    database='premier_league'
)
cursor = conn.cursor()

def insert_dataframe(df, table_name):
    placeholders = ', '.join(['%s'] * len(df.columns))
    columns = ', '.join(df.columns)
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    for row in df.itertuples(index=False, name=None):
        # nan to none
        cleaned_row = tuple(None if pd.isna(x) else x for x in row)
        cursor.execute(sql, cleaned_row)

venue_df = pd.read_csv('venue.csv')
insert_dataframe(venue_df, 'venue')

club_df = pd.read_csv('club.csv')
insert_dataframe(club_df, 'club')

club_member_df = pd.read_csv('club_member.csv')
insert_dataframe(club_member_df, 'club_member')

player_df = pd.read_csv('player.csv')
insert_dataframe(player_df, 'player')

manager_df = pd.read_csv('manager.csv')
insert_dataframe(manager_df, 'manager')

contract_df = pd.read_csv('contract.csv')
insert_dataframe(contract_df, 'contract')

fixture_df = pd.read_csv('fixture.csv')
insert_dataframe(fixture_df, 'fixture')

club_stat_df = pd.read_csv('club_stat.csv')
insert_dataframe(club_stat_df, 'club_stat')

goal_df = pd.read_csv('goal.csv')
insert_dataframe(goal_df, 'goal')

player_stat_df = pd.read_csv('player_stat.csv')
insert_dataframe(player_stat_df, 'player_stat')

conn.commit()
cursor.close()
conn.close()

print("CSVs inserted into MySQL database successfully.")
