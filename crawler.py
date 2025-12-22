import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin, urlparse

MAX_PAGES = 50
DATA_DIR = "data"

if not os.path.exists (DATA_DIR) :
    os.makedirs(DATA_DIR)

#gets the page to use 
def fetch_page(url):
    print(f"🕷️  Crawling: {url}")
    try: 
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.text
        else:
            return None
        
    except Exception as e:
        print(f"Error in the file: {e}")
        return None

def parse_links(html, current_url, allowed_domain):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for link in soup.find_all('a', href = True):
        href = link["href"]
        if not href or href.startswith('#') or href.startswith('javascript:'):
            continue 
        full_url = urljoin(current_url, href)
        full_url = full_url.rstrip('/')
        if allowed_domain in full_url:
            links.add(full_url)
    
    return links

def save_text(url, html, doc_id):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator = ' ', strip= True)
    filename = os.path.join(DATA_DIR, f"doc_{doc_id}.txt")
    with open(filename,'w', encoding='utf-8') as f:
        f.write(url + "\n\n" + text)
    print(f"💾 Saved: doc_{doc_id}.txt")

def crawl(start_url, allowed_domain):
    queue = [start_url]
    visited = set()
    count = 0
    while queue and count < MAX_PAGES :
        url = queue.pop(0)
        if url in visited:
            continue 
        visited.add(url)
    html = fetch_page(url)
    if html is not None:
        save_text(url, html, count)
        count += 1
        new_links = parse_links(html, url, allowed_domain)
        for link in new_links:
            if link not in visited and link not in queue:
                queue.append(link)
        time.sleep(1)

if __name__ == "__main__":
    user_url = input("Enter a website to crawl (include https://): ")
    domain = urlparse(user_url).netloc
    print(f"--- Crawling Domain: {domain} ---")
    crawl(user_url, domain)
