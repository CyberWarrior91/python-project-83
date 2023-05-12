from urllib.parse import urlparse


def normalize_url(url):
    url_scheme = urlparse(url).scheme
    url_netloc = urlparse(url).netloc
    curr_url = f'{url_scheme}://{url_netloc}'
    return curr_url