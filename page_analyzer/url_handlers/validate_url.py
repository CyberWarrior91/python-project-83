import validators


def validate(url):
    errors = {}
    if not validators.url(url):
        errors['wrong'] = 'Некорректный URL'
    if url == '':
        errors['blank'] = 'URL обязателен'
    return errors
