import random
import requests
from bs4 import BeautifulSoup
import time


def get_nature_links(keyword):
    keyword = "microbiome and " + keyword
    search_url = f"https://www.nature.com/search?q={keyword.replace(' ', '+')}&article_type=research&order=relevance"
    response = requests.get(search_url)
    time.sleep(3)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        title = a.get_text().strip()
        url = a['href']
        if url.startswith('/articles/') and keyword.lower() in title.lower():
            full_url = f"https://www.nature.com{url}"
            links.append([title, full_url])
    return links


def get_biomedcentral_links(keyword):
    keyword = "microbiome and " + keyword
    search_url = f"https://www.biomedcentral.com/search?query={keyword.replace(' ', '+')}"
    response = requests.get(search_url)
    time.sleep(3)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        title = a.get_text().strip()
        url = a['href']
        if ('/articles/' in url) and ('/supplements/' not in url) and ('Full Text' not in title) and keyword.lower() in title.lower():
            full_url = f"https:{url}"
            links.append([title, full_url])
    return links


def get_microbiologyresearch_links(keyword):
    keyword = "microbiome and " + keyword
    search_url = f"https://www.microbiologyresearch.org/search?value1={keyword.replace(' ', '+')}&option1=fulltext"
    response = requests.get(search_url)
    time.sleep(3)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        title = a.get_text().strip()
        url = a['href']
        if ('/content/journal/' in url) and ('read more' not in title.lower()) and (len(title)>15) and keyword.lower() in title.lower():
            full_url = f"https://www.microbiologyresearch.org{url}"
            links.append([title, full_url])
    return links


def get_mdpi_links(keyword):
    keyword = "microbiome and " + keyword
    search_url = f"https://www.mdpi.com/search?q={keyword.replace(' ', '+')}"
    response = requests.get(search_url)
    time.sleep(3)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for article in soup.find_all('div', class_='article-item'):
        a = article.find('a', class_='title-link', href=True)
        if a:
            title = a.get_text().strip()
            url = a['href']
            if not url.startswith('http') and keyword.lower() in title.lower():
                url = f"https://www.mdpi.com{url}"
            links.append([title, url])
    return links


def get_cambridge_links(keyword):
    keyword = "microbiome and " + keyword
    search_url = f"https://www.cambridge.org/core/journals/epidemiology-and-infection/listing?q={keyword.replace(' ', '+')}"
    response = requests.get(search_url)
    time.sleep(3)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        title = a.get_text().strip()
        url = a['href']
        if ('/core/journals/' in url) and ('/article/' in url) and (len(title)>15) and keyword.lower() in title.lower():
            full_url = f"https://www.cambridge.org{url}"
            links.append([title, full_url])
    return links


def get_mixed_links(keyword, randomize=False):
    links = get_nature_links(keyword)
    links.extend(get_microbiologyresearch_links(keyword))
    links.extend(get_mdpi_links(keyword))
    links.extend(get_biomedcentral_links(keyword))
    links.extend(get_cambridge_links(keyword))
    if randomize:
        random.shuffle(links)
    return links
