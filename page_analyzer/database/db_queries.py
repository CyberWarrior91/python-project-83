import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

"""Connect to database and return Python dictionary object"""

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
CONNECTION = psycopg2.connect(DATABASE_URL)


def check_url_in_table(url):
    """Check whether the URL is already in database or not"""
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
        curs.execute("""SELECT * FROM urls WHERE name=%s""", (url, ))
        url_record = curs.fetchone()
    if url_record:
        return True


def select_from_urls(value):
    conn = psycopg2.connect(DATABASE_URL)
    attr = 'id' if value.isdigit() else 'name'
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
        curs.execute(f"""SELECT * FROM urls WHERE {attr}=%s""", (value, ))
        return curs.fetchone()


def select_from_url_checks(value):
    conn = psycopg2.connect(DATABASE_URL)
    attr = 'name' if value.isalpha() else 'url_id'
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
        curs.execute(f"""SELECT * FROM url_checks WHERE {attr}=%s""", (value, ))
        return curs.fetchall()


def select_complex():
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
        curs.execute("""SELECT urls.id, urls.name,
                  url_checks.created_at, url_checks.status_code
                FROM urls
                LEFT JOIN (
                SELECT url_id, MAX(created_at) as created_at,
                    url_checks.status_code
                FROM url_checks
                GROUP BY url_id, url_checks.status_code
                ) url_checks ON urls.id = url_checks.url_id""")
        result = curs.fetchall()
    return result


def insert_to_urls(values):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as curs:
        curs.execute("""INSERT INTO urls (name, created_at)
        VALUES (%s, %s)""", (values))
        conn.commit()


def insert_to_url_checks(values):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as curs:
        curs.execute("""INSERT INTO url_checks (url_id, h1, title,
            description, status_code, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)""", (values))
        conn.commit()
