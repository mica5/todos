from contextlib import contextmanager

import psycopg2

@contextmanager
def get_connection(connection_string):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    yield conn, cursor

    cursor.close()
    conn.close()

