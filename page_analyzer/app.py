from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    get_flashed_messages,
    flash)
from dotenv import load_dotenv
import os
import psycopg2
import psycopg2.extras
import validators
from datetime import date
from urllib.parse import urlparse


app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def main():
    messages = get_flashed_messages(with_categories=True)
    return render_template('main.html', messages=messages)


def validation(url):
    errors = {}
    if url == '':
        errors['blank_url'] = 'URL обязателен'
    if not validators.url(url):
        errors['wrong_url'] = 'Некорректный URL'
    return errors


@app.route('/urls', methods=['GET', 'POST'])
def handle_urls():
    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    if request.method == 'POST':
        new_url = request.form.get("url")
        if new_url == '':
            flash('Некорректный URL')
            flash('URL обязателен')
            return redirect(url_for('main'), code=302)
        if validators.url(new_url):
            url_scheme = urlparse(new_url).scheme
            url_netloc = urlparse(new_url).netloc
            curr_url = f'{url_scheme}://{url_netloc}'
            with conn.cursor() as curs:
                try:
                    curs.execute("""SELECT id FROM urls WHERE name=%s""",
                                 (curr_url, ))
                    url_id = curs.fetchone()[0]
                    flash('Страница уже существует', 'repeat')
                    return redirect(url_for('url_page', id=url_id), code=302)
                except Exception:
                    curs.execute(
                        """INSERT INTO urls (name, created_at)
                        VALUES (%s, %s);""",
                        (curr_url, date.today()))
                    conn.commit()
            with conn.cursor() as curs:
                curs.execute("""SELECT id FROM urls WHERE name=%s""",
                             (curr_url, ))
                url_id = curs.fetchone()[0]
            curs.close()
            conn.close()
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('url_page', id=url_id), code=302)
        else:
            flash('Некорректный URL')
            return redirect(url_for('main'), code=302)
    if request.method == 'GET':
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
            curs.execute(
                """SELECT urls.id, urls.name, url_checks.created_at
                FROM urls
                LEFT JOIN (
                SELECT url_id, MAX(created_at) as created_at
                FROM url_checks
                GROUP BY url_id
                ) url_checks ON urls.id = url_checks.url_id""")
            urls_base = curs.fetchall()
        curs.close()
        conn.close()
        return render_template('all_urls.html', urls=urls_base)


@app.get('/urls/<id>')
def url_page(id):
    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    messages = get_flashed_messages(with_categories=True)
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
        curs.execute(
            """SELECT id, name, created_at
            FROM urls WHERE id=%s""", (id, ))
        url = curs.fetchone()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
        curs.execute(
            """SELECT id, created_at FROM url_checks
            WHERE url_id=%s""", (id, ))
        check_info = curs.fetchall()
    curs.close()
    conn.close()
    return render_template(
        'single_url.html',
        check_info=check_info, messages=messages, url=url)


@app.post('/urls/<id>/checks')
def make_check(id):
    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as curs:
        curs.execute(
            """INSERT INTO url_checks (url_id, created_at)
            VALUES (%s, %s)""", (id, date.today()))
        conn.commit()
    curs.close()
    conn.close()
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('url_page', id=id), code=302)
