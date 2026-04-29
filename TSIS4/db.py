from datetime import datetime

from psycopg2 import OperationalError

from connect import connect


def initialize_database():
    query = """
    CREATE TABLE IF NOT EXISTS players (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS game_sessions (
        id SERIAL PRIMARY KEY,
        player_id INTEGER REFERENCES players(id),
        score INTEGER NOT NULL,
        level_reached INTEGER NOT NULL,
        played_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    """
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
    except OperationalError:
        return False
    return True


def get_or_create_player(username):
    query = """
    INSERT INTO players (username)
    VALUES (%s)
    ON CONFLICT (username) DO UPDATE SET username = EXCLUDED.username
    RETURNING id
    """
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (username,))
            return cur.fetchone()[0]


def save_game_result(username, score, level_reached):
    query = """
    INSERT INTO game_sessions (player_id, score, level_reached, played_at)
    VALUES (%s, %s, %s, %s)
    """
    try:
        player_id = get_or_create_player(username)
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (player_id, score, level_reached, datetime.now()))
    except OperationalError:
        return False
    return True


def fetch_top_scores():
    query = """
    SELECT p.username, g.score, g.level_reached, g.played_at
    FROM game_sessions g
    JOIN players p ON p.id = g.player_id
    ORDER BY g.score DESC, g.level_reached DESC, g.played_at ASC
    LIMIT 10
    """
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()
    except OperationalError:
        return []


def fetch_personal_best(username):
    query = """
    SELECT COALESCE(MAX(g.score), 0)
    FROM game_sessions g
    JOIN players p ON p.id = g.player_id
    WHERE p.username = %s
    """
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (username,))
                result = cur.fetchone()
                return result[0] if result else 0
    except OperationalError:
        return 0
