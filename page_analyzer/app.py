from flask import (
    Flask,
    render_template,
    request,
    redirect,
    make_response,
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
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def main():
    messages = get_flashed_messages(with_categories=True)
    return render_template('main.html', messages=messages)


@app.route('/urls', methods=['GET', 'POST'])
def handle_urls():
    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    if request.method == 'POST':
        new_url = request.form.get("url")
        if new_url == '':
            flash('Некорректный URL')
            flash('URL обязателен')
            messages = get_flashed_messages(with_categories=True)
            return render_template(
                'main.html', messages=messages), 422
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
            value = new_url
            messages = get_flashed_messages(with_categories=True)
            return render_template(
                'main.html', value=value, messages=messages), 422

    if request.method == 'GET':
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
            curs.execute(
                """SELECT urls.id, urls.name,
                url_checks.created_at, url_checks.status_code
                FROM urls
                LEFT JOIN (
                SELECT url_id, MAX(created_at) as created_at,
                url_checks.status_code
                FROM url_checks
                GROUP BY url_id, url_checks.status_code
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
            """SELECT
            id, status_code, h1, title, description, created_at
            FROM url_checks
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
            """SELECT name
            FROM urls WHERE id=%s""", (id, ))
        website = curs.fetchone()[0]
        try:
            request = requests.get(website)
            response = make_response(redirect(url_for('url_page', id=id), code=302))
            response.raise_for_status()
        except Exception:
            flash('Произошла ошибка при проверке', 'danger')
            return redirect(url_for('url_page', id=id), code=302)
    with conn.cursor() as curs:
        status_code = request.status_code
        soup = BeautifulSoup(request.text, 'html.parser')
        title = soup.title.string
        h1 = soup.h1.string if soup.find('h1') else ''
        meta = soup.find(attrs={'name': 'description'})
        description = meta.get('content') if meta else ''
        curs.execute(
            """INSERT INTO url_checks
            (url_id, status_code, h1, title, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (id, status_code, h1, title, description, date.today()))
        conn.commit()
    curs.close()
    conn.close()
    flash('Страница успешно проверена', 'success')
    return response
