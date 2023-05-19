import validators
"""Validate the correction of URL name"""


def validate(url):
    errors = {}
    if not validators.url(url):
        errors['wrong'] = 'Некорректный URL'
    if url == '':
        errors['blank'] = 'URL обязателен'
        errors['wrong'] = 'Некорректный URL'
    if len(url) > 255:
        errors['too_long'] = 'URL превышает 255 символов'
    return errors
