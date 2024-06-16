import requests
from bs4 import BeautifulSoup
import time


def get_nature_links(keyword):
    search_url = f"https://www.nature.com/search?q={keyword.replace(' ', '+')}&article_type=research&order=relevance"
    response = requests.get(search_url)
    time.sleep(3)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        title = a.get_text().strip()
        url = a['href']
        if url.startswith('/articles/'):
            full_url = f"https://www.nature.com{url}"
            links.append([title, full_url])
    return links


# How to use the above:
#keyword = "microbiome and hypertension"
#links = get_nature_links(keyword)
#for idx, (title, url) in enumerate(links[:10]):
#    print(f"{idx + 1}. **{title}**: {url}")
