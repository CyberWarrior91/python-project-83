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
import requests
from page_analyzer.parse_url import parse_parameters
from page_analyzer.normalize_url import normalize_url
from page_analyzer.db_functions import select, insert, select_complex


app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def main():
    messages = get_flashed_messages(with_categories=True)
    return render_template('main.html', messages=messages)


@app.route('/urls', methods=['GET', 'POST'])
def handle_urls():
    if request.method == 'POST':
        new_url = request.form.get("url")
        if new_url == '':
            flash('Некорректный URL')
            flash('URL обязателен')
            messages = get_flashed_messages(with_categories=True)
            return render_template(
                'main.html', messages=messages), 422
        if validators.url(new_url):
            curr_url = normalize_url(new_url)
            try:
                url_id = select(['id'], 'urls', 'name', curr_url)[0]
                flash('Страница уже существует', 'repeat')
                return redirect(url_for('url_page', id=url_id), code=302)
            except Exception:
                insert(
                    'urls', ['name', 'created_at'], 
                    [curr_url, date.today().__str__()]
                    )
            url_id = select(['id'], 'urls', 'name', curr_url)[0]
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('url_page', id=url_id), code=302)
        else:
            flash('Некорректный URL')
            value = new_url
            messages = get_flashed_messages(with_categories=True)
            return render_template(
                'main.html', value=value, messages=messages), 422
    if request.method == 'GET':
        urls = select_complex(
            data=['urls.id', 'urls.name', 'url_checks.created_at', 'url_checks.status_code'],
            join_type='LEFT JOIN',
            sub_data=['url_id', 'MAX(created_at) as created_at', 'url_checks.status_code'],
            group_by=['url_id' , 'url_checks.status_code'],
            table_1='urls', table_2='url_checks',
            equality='urls.id = url_checks.url_id'
            )
        return render_template('all_urls.html', urls=urls)


@app.get('/urls/<id>')
def url_page(id):
    messages = get_flashed_messages(with_categories=True)
    url = select(['id', 'name', 'created_at'], 'urls', 'id', id)
    check_info = select(
        ['id', 'status_code', 'h1', 'title', 'description', 'created_at'],
        'url_checks',
        'url_id', id, fetch="Many")
    return render_template(
        'single_url.html',
        check_info=check_info, messages=messages, url=url)


def make_request(url):
    return requests.get(url)


@app.post('/urls/<id>/checks')
def make_check(id):
    website = select(['name'], 'urls', 'id', id)[0]
    try:
        response = make_request(website)
        response.raise_for_status()
    except Exception:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('url_page', id=id), code=302)
    status_code = response.status_code
    title, h1, description = parse_parameters(response)
    insert('url_checks', 
           ['url_id', 'h1', 'title', 'description', 'status_code', 'created_at'],
           [str(id), h1, title, description, str(status_code), date.today().__str__()]
            )
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('url_page', id=id), code=302)
