import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)


def select(data: list, table, attr, value, fetch='One'):
    data_string = (', ').join(data)
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
        curs.execute(
            f"""SELECT {data_string} FROM {table}
            WHERE {attr}=%s""", (value, ))
        if fetch == 'Many':
            return curs.fetchall()
        return curs.fetchone()


def select_complex(
        data: list = [], sub_data: list = [], group_by: list = [],
        table_1: str = '', table_2: str = '', equality: str = '',
        join_type='INNER JOIN'):
    data_str = (', ').join(data)
    sub_data_str = (', ').join(sub_data)
    group_by_str = (', ').join(group_by)
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
        curs.execute(f"""SELECT {data_str}
                FROM {table_1}
                {join_type} (
                SELECT {sub_data_str}
                FROM {table_2}
                GROUP BY {group_by_str}
                ) {table_2} ON {equality}""")
        result = curs.fetchall()
    return result


def insert(table, attrs: list, values: list):
    attrs_str = (', ').join(attrs)
    pseudo_values = values[:]
    for i in range(len(pseudo_values)):
        pseudo_values[i] = '%s'
    values_count = (', ').join(pseudo_values)
    with conn.cursor() as curs:
        curs.execute(
            f"""INSERT INTO {table}
            ({attrs_str})
            VALUES ({values_count})""",
            (values))
        conn.commit()
