import psycopg2

from config import load_config


def connect():
    """
    creates a connection to the PostgreSQL database and returns the connection object.
        does not use with statement, so the caller is responsible for closing the connection.
    """
    config = load_config()
    return psycopg2.connect(**config)
