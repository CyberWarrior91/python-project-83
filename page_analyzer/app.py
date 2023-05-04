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
try:
    # пытаемся подключиться к базе данных
    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
    print('Can`t establish connection to database')

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
            curr_url = f'{urlparse(new_url).scheme}://{urlparse(new_url).netloc}'
            with conn.cursor() as curs:
                try:
                    curs.execute("""SELECT id FROM urls WHERE name=%s""", (curr_url, ))
                    url_id = curs.fetchone()[0]
                    flash('Страница уже существует')
                    return redirect(url_for('url_page', id=url_id), code=302)
                except:
                    curs.execute("""INSERT INTO urls (name, created_at) VALUES (%s, %s);""", (curr_url, date.today()))
                    conn.commit()
            with conn.cursor() as curs:
                curs.execute("""SELECT id FROM urls WHERE name=%s""", (curr_url, ))
                url_id = curs.fetchone()[0]
            curs.close()
            conn.close()
            flash('Страница успешно добавлена')
            return redirect(url_for('url_page', id=url_id), code=302)
        else:
            flash('Некорректный URL')
            return redirect(url_for('main'), code=302)


    if request.method == 'GET':
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
            curs.execute("""SELECT id, name, created_at FROM urls""")
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
        curs.execute("""SELECT id, name, created_at FROM urls WHERE id=%s""", (id, ))
        url = curs.fetchone()
    curs.close()
    conn.close()
    return render_template('single_url.html', messages=messages, url=url)

