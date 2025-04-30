CREATE DATABASE premier_league;
USE premier_league;

CREATE TABLE venue (
    name VARCHAR(100) PRIMARY KEY,
    city VARCHAR(100),
    capacity INT,
    year_opened INT
);

CREATE TABLE club (
    name VARCHAR(100) PRIMARY KEY,
    founding_year INT,
    stadium VARCHAR(100) UNIQUE,
    FOREIGN KEY (stadium) REFERENCES venue(name)
);

CREATE TABLE club_member (
    member_id INT PRIMARY KEY,
    name VARCHAR(100),
    date_of_birth DATE,
    nationality VARCHAR(50),
    club VARCHAR(100),
    height DECIMAL(3,2),
    FOREIGN KEY (club) REFERENCES club(name)
);

CREATE TABLE player (
    member_id INT PRIMARY KEY,
    position VARCHAR(50),
    shirt_number INT,
    market_value_euros DECIMAL(10,2),
    FOREIGN KEY (member_id) REFERENCES club_member(member_id)
);

CREATE TABLE manager (
    member_id INT PRIMARY KEY,
    titles INT,
    years_of_service INT,
    FOREIGN KEY (member_id) REFERENCES club_member(member_id)
);

CREATE TABLE contract (
    member_id INT PRIMARY KEY,
    start_date DATE,
    weekly_wage_pounds DECIMAL(10,2),
    end_date DATE,
    FOREIGN KEY (member_id) REFERENCES club_member(member_id)
);

CREATE TABLE fixture (
    match_id INT PRIMARY KEY,
    date DATE,
    home_club VARCHAR(100),
    away_club VARCHAR(100),
    FOREIGN KEY (home_club) REFERENCES club(name),
    FOREIGN KEY (away_club) REFERENCES club(name)
);

CREATE TABLE club_stat (
    club_stat_id INT PRIMARY KEY,
    match_id INT,
    club VARCHAR(100),
    goals_scored INT,
    possession DECIMAL(5,2),
    FOREIGN KEY (club) REFERENCES club(name),
    FOREIGN KEY (match_id) REFERENCES fixture(match_id)
);

CREATE TABLE goal (
    goal_id INT PRIMARY KEY,
    minute INT,
    half INT,
    xg DECIMAL(4,2),
    psxg DECIMAL(4,2),
    yards_out INT,
    body_part ENUM('Left Foot', 'Right Foot', 'Head', 'Other') DEFAULT 'Other',
    method ENUM('Open Play', 'Penalty', 'Free Kick'),
    match_id INT,
    scorer_id INT,
    assist_id INT,
    club VARCHAR(100),
    FOREIGN KEY (match_id) REFERENCES fixture(match_id),
    FOREIGN KEY (scorer_id) REFERENCES club_member(member_id),
    FOREIGN KEY (assist_id) REFERENCES club_member(member_id),
    FOREIGN KEY (club) REFERENCES club(name)
);

CREATE TABLE player_stat (
    stat_id INT PRIMARY KEY,
    match_id INT,
    member_id INT,
    minutes INT,
    goals INT,
    assists INT,
    pens_made INT,
    pens_attempted INT,
    shots_attempted INT,
    shots_on_target INT,
    yellow_cards INT,
    red_cards INT,
    touches INT,
    tackles INT,
    interceptions INT,
    blocks INT,
    xg DECIMAL(4,2),
    xa DECIMAL(4,2),
    passes_attempted INT,
    passes_completed INT,
    dribbles_attempted INT,
    dribbles_completed INT,
    crosses INT,
    throw_ins INT,
    corner_kicks INT,
    shots_blocked INT,
    passes_blocked INT,
    clearances INT,
    fouls_committed INT,
    fouls_drawn INT,
    offsides INT,
    pens_won INT,
    pens_conceded INT,
    own_goals INT,
    shot_creating_actions INT,
    goal_creating_actions INT,
    recoveries INT,
    aeriel_duels_won INT,
    aeriel_duels_lost INT,
    sot_against INT,
    goals_against INT,
    saves INT,
    psxg_against DECIMAL(4,2),
    subbed_in BOOLEAN,
    subbed_off BOOLEAN,
    started BOOLEAN,
    FOREIGN KEY (match_id) REFERENCES fixture(match_id),
    FOREIGN KEY (member_id) REFERENCES club_member(member_id)
);
