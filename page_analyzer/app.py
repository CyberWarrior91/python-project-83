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
from datetime import date
import requests
from page_analyzer.database.db_queries import (
    select_from_urls,
    select_complex,
    select_from_url_checks,
    insert_to_urls,
    insert_to_url_checks)
from page_analyzer.url_handlers.parse_url import parse_parameters
from page_analyzer.url_handlers.normalize_url import normalize_url
from page_analyzer.url_handlers.validate_url import validate


app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def main():
    messages = get_flashed_messages(with_categories=True)
    return render_template('main.html', messages=messages)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('server_error.html'), 500


@app.route('/urls', methods=['GET', 'POST'])
def handle_urls():
    if request.method == 'POST':
        """Handle the URL from main page input and add it to 'urls' table"""
        new_url = request.form.get("url")
        errors = validate(new_url)
        if not errors:
            curr_url = normalize_url(new_url)
            try:
                url_id = select_from_urls(curr_url)['id']
                flash('Страница уже существует', 'repeat')
                return redirect(url_for('url_page', id=url_id), code=302)
            except Exception:
                creation_date = date.today().__str__()
                insert_to_urls([curr_url, creation_date])
            url_id = select_from_urls(curr_url)['id']
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('url_page', id=url_id), code=302)
        if 'wrong' and 'blank' in errors.keys():
            flash(errors['wrong'])
            flash(errors['blank'])
            messages = get_flashed_messages(with_categories=True)
            return render_template(
                'main.html', messages=messages), 422
        if 'too_long' in errors.keys():
            flash(errors['too_long'])
            messages = get_flashed_messages(with_categories=True)
            return render_template(
                'main.html', messages=messages), 422
        else:
            flash(errors['wrong'])
            value = new_url
            messages = get_flashed_messages(with_categories=True)
            return render_template(
                'main.html', value=value, messages=messages), 422
    if request.method == 'GET':
        """Show the whole list of URLS in database,
        compiling urls and url_checks tables"""
        urls = select_complex()
        return render_template('all_urls.html', urls=urls)


@app.get('/urls/<id>')
def url_page(id):
    """Show the data for specific url id"""
    messages = get_flashed_messages(with_categories=True)
    url = select_from_urls(id)
    check_info = select_from_url_checks(id)
    return render_template(
        'single_url.html',
        check_info=check_info, messages=messages, url=url)


def make_request(url):
    response = requests.get(url)
    response.raise_for_status()
    return response


@app.post('/urls/<id>/checks')
def make_check(id):
    """Make a check-out of a specific url, parse basic HTML info"""
    website = select_from_urls(id)['name']
    try:
        response = make_request(website)
    except Exception:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('url_page', id=id), code=302)
    status_code = response.status_code
    title, h1, description = parse_parameters(response)
    check_date = date.today().__str__()
    insert_to_url_checks([str(id), h1, title, description,
                          str(status_code), check_date])
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('url_page', id=id), code=302)
