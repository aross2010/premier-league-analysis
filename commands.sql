-- BASIC SQL:

-- rank venues by how long they've been open
SELECT 
    name,
    city,
    year_opened
FROM venue
ORDER BY year_opened ASC;

-- get the number of spanish club members (players and managers)
SELECT COUNT(*) AS spanish_members
FROM club_member
WHERE nationality = 'Spain';

-- get the number of goals outside the box
SELECT COUNT(*) AS goals_outside_box
FROM goal
WHERE yards_out > 18;

-- get the club that scored the most goals in a single match
SELECT club, goals_scored
FROM club_stat
ORDER BY goals_scored DESC
LIMIT 1;

-- rank clubs by their average possession
SELECT 
    club, 
    ROUND(AVG(possession), 2) AS avg_possession_percentage
FROM club_stat
GROUP BY club
ORDER BY avg_possession_percentage DESC;

-- INTERMEDIATE SQL:

-- rank players by the number of goals they scored
SELECT 
    cm.name,
    p.position,
    cm.club,
    COALESCE(SUM(ps.goals), 0) AS total_goals
FROM club_member cm
JOIN player p ON cm.member_id = p.member_id
JOIN player_stat ps ON cm.member_id = ps.member_id
GROUP BY cm.name, p.position, cm.club
ORDER BY total_goals DESC

-- get the most expensive player in the league
SELECT 
    cm.name,
    c.weekly_wage_pounds
FROM club_member cm
JOIN contract c ON cm.member_id = c.member_id
JOIN player p ON cm.member_id = p.member_id
ORDER BY c.weekly_wage_pounds DESC
LIMIT 1;

-- rank players by the number of goals they scored as a substitute
SELECT 
    cm.name,
    p.position,
    p.market_value_euros,
    cm.club,
    SUM(ps.goals) AS goals_as_sub
FROM player_stat ps
JOIN club_member cm ON ps.member_id = cm.member_id
JOIN player p ON ps.member_id = p.member_id
WHERE ps.subbed_in = TRUE
GROUP BY cm.name, p.position, p.market_value_euros, cm.club
ORDER BY goals_as_sub DESC;

-- rank players by the number of goal contributions (goals + assists)
SELECT 
    cm.name, 
    p.position, 
    p.market_value_euros,
    TIMESTAMPDIFF(YEAR, cm.date_of_birth, '2023-08-11') AS age_at_season_start, 
    COALESCE(SUM(ps.goals + ps.assists), 0) AS goal_contributions
FROM club_member cm
JOIN player p ON cm.member_id = p.member_id
JOIN player_stat ps ON cm.member_id = ps.member_id
GROUP BY cm.name, p.position, p.market_value_euros, age_at_season_start
ORDER BY goal_contributions DESC;

-- rank clubs by the number of points obtained (win: 3, draw: 1, gd: tiebreaker)
SELECT 
    c.name AS club_name,
    COUNT(cs.match_id) AS games_played,
    SUM(
        CASE 
            WHEN cs.goals_scored > opp.goals_scored THEN 1 
            ELSE 0 
        END
    ) AS wins,
    SUM(
        CASE 
            WHEN cs.goals_scored = opp.goals_scored THEN 1 
            ELSE 0 
        END
    ) AS draws,
    SUM(
        CASE 
            WHEN cs.goals_scored < opp.goals_scored THEN 1 
            ELSE 0 
        END
    ) AS losses,
    SUM(
        CASE 
            WHEN cs.goals_scored > opp.goals_scored THEN 3
            WHEN cs.goals_scored = opp.goals_scored THEN 1
            ELSE 0
        END
    ) AS points,
    SUM(cs.goals_scored - opp.goals_scored) AS goal_difference
FROM club c
JOIN club_stat cs ON c.name = cs.club
JOIN club_stat opp ON cs.match_id = opp.match_id AND cs.club != opp.club
GROUP BY c.name
ORDER BY points DESC, goal_difference DESC;

-- ADVANCED SQL:

-- get the club who underperformed the most in terms of xG vs goals scored
WITH club_goals AS (
    SELECT
        cs.match_id,
        cs.club,
        SUM(cs.goals_scored) AS match_goals
    FROM club_stat cs
    GROUP BY cs.match_id, cs.club
),
club_xg AS (
    SELECT
        cm.club,
        ps.match_id,
        SUM(ps.xg) AS match_xg
    FROM player_stat ps
    JOIN club_member cm ON ps.member_id = cm.member_id
    GROUP BY cm.club, ps.match_id
)
SELECT
    cx.club,
    ROUND(SUM(cx.match_xg), 2) AS total_xg,
    SUM(cg.match_goals) AS total_goals,
    ROUND(SUM(cx.match_xg) - SUM(cg.match_goals), 2) AS xg_minus_goals
FROM club_xg cx
JOIN club_goals cg ON cx.club = cg.club AND cx.match_id = cg.match_id
GROUP BY cx.club
ORDER BY xg_minus_goals DESC
LIMIT 1;

-- rank players by their overperformance in terms of xG vs goals scored
SELECT 
    finishers.name,
    finishers.position,
    finishers.club,
    c.founding_year,
    finishers.total_goals,
    finishers.total_xg,
    (finishers.total_goals - finishers.total_xg) AS overperformance
FROM (
    SELECT 
        cm.name,
        p.position,
        cm.club,
        SUM(ps.goals) AS total_goals,
        SUM(ps.xg) AS total_xg
    FROM player_stat ps
    JOIN club_member cm ON ps.member_id = cm.member_id
    JOIN player p ON ps.member_id = p.member_id
    GROUP BY cm.name, p.position, cm.club
) AS finishers
JOIN club c ON finishers.club = c.name
WHERE finishers.total_xg >= 5
ORDER BY overperformance DESC;

-- rank players by the number of shot-creating actions (SCA)
SELECT 
    cm.name,
    cm.club,
    p.position,
    sca_top.total_sca
FROM (
    SELECT 
        ps.member_id,
        SUM(ps.shot_creating_actions) AS total_sca
    FROM player_stat ps
    JOIN player p2 ON ps.member_id = p2.member_id
    GROUP BY ps.member_id
) AS sca_top
JOIN club_member cm ON sca_top.member_id = cm.member_id
JOIN player p ON sca_top.member_id = p.member_id
ORDER BY sca_top.total_sca DESC;

-- rank defenders & midfielders by their defensive actions
SELECT 
    cm.name,
    cm.club,
    p.position,
    defender_stats.defensive_score
FROM club_member cm
JOIN (
    SELECT 
        ps.member_id,
        SUM(ps.tackles + ps.interceptions + ps.blocks + ps.clearances + ps.shots_blocked + ps.passes_blocked + ps.ariel_duels_won) AS defensive_score
    FROM player_stat ps
    JOIN player p2 ON ps.member_id = p2.member_id
    WHERE p2.position IN ('Defender', 'Midfielder')
    GROUP BY ps.member_id
) AS defender_stats ON cm.member_id = defender_stats.member_id
JOIN player p ON cm.member_id = p.member_id
ORDER BY defender_stats.defensive_score DESC;

-- rank goalkeepers by their overperformance in terms of goals against vs PSxG against
SELECT 
    cm.name,
    cm.club,
    p.position,
    gk_stats.total_saves,
    gk_stats.total_goals_against,
    gk_stats.total_psxg_against,
    (gk_stats.total_psxg_against - gk_stats.total_goals_against) AS overperformance
FROM club_member cm
JOIN (
    SELECT 
        ps.member_id,
        SUM(ps.saves) AS total_saves,
        SUM(ps.goals_against) AS total_goals_against,
        SUM(ps.psxg_against) AS total_psxg_against
    FROM player_stat ps
    JOIN player p2 ON ps.member_id = p2.member_id   
    WHERE p2.position = 'Goalkeeper'                
    GROUP BY ps.member_id
    HAVING SUM(ps.saves) >= 50
) AS gk_stats ON cm.member_id = gk_stats.member_id
JOIN player p ON p.member_id = cm.member_id
ORDER BY overperformance DESC;