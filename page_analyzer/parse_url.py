from bs4 import BeautifulSoup


def parse_parameters(url):
    soup = BeautifulSoup(url.text, 'html.parser')
    title = soup.title.string
    h1 = soup.h1.string if soup.find('h1') else ''
    meta = soup.find(attrs={'name': 'description'})
    description = meta.get('content') if meta else ''
    return title, h1, description