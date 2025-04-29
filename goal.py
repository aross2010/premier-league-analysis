# go back and add the half column & convert minute to int in the goal.csv file
import pandas as pd

goal_df = pd.read_csv('goal.csv')

def process_minute(minute):
    if isinstance(minute, str) and '+' in minute:
        base, extra = minute.split('+')
        minute_int = int(base) + int(extra)
        if base == '45':
            half = 1
        elif base == '90':
            half = 2
        else:
            half = 1 if int(base) <= 45 else 2
    else:
        minute_int = int(minute)
        half = 1 if minute_int <= 45 else 2
    return minute_int, half

goal_df[['minute', 'half']] = goal_df['minute'].apply(lambda x: pd.Series(process_minute(x)))

goal_df.to_csv('goal.csv', index=False)