from bs4 import BeautifulSoup
"""Parse Url via BeautifulSoup library and return basic html data"""


def parse_parameters(url):
    soup = BeautifulSoup(url.text, 'html.parser')
    title = soup.title.string if soup.find('title') else ''
    h1 = soup.h1.string if soup.find('h1') else ''
    meta = soup.find(attrs={'name': 'description'})
    description = meta.get('content') if meta else ''
    if len(description) >= 255:
        new_description = description[:255]
        return title, h1, new_description
    return title, h1, description
