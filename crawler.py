import requests
from bs4 import BeautifulSoup
import time
import os
import re
from urllib.parse import urljoin, urlparse



MAX_PAGES = 20
MAX_DEPTH = 2
CRAWL_DELAY = 0.0001
DATA_DIR = "data"
SEED_URLS = [
    "https://www.caranddriver.com/news/",
    "https://www.motortrend.com/news/",
    "https://www.autoweek.com/news/",
    "https://www.thedrive.com/news/",
    "https://en.wikipedia.org/wiki/Electric_vehicle",
    "https://en.wikipedia.org/wiki/Electric_car",
    "https://en.wikipedia.org/wiki/Hybrid_vehicle",
    "https://en.wikipedia.org/wiki/Automotive_industry",
    "https://en.wikipedia.org/wiki/Tesla,_Inc.",
    "https://en.wikipedia.org/wiki/Ford_Motor_Company",
    "https://en.wikipedia.org/wiki/General_Motors",
]
AUTOMOTIVE_KEYWORDS = [
    'electric', 'vehicle', 'car', 'battery', 
    'automobile', 'automotive', 'ev', 'tesla', 
    'ford', 'gm', 'toyota', 'nissan', 'charging',
    'motor', 'engineering', 'technology'
]
BLACKLISTED_DOMAINS = [
    'quotes.toscrape.com',
    'example.com',
    'placeholder.com',
    'toscrape.com',
    'example.com',
    'sample.com'
]


def is_valid_domain(url):
    parsed_url = urlparse(url)
    return not any(blocked in parsed_url.netloc for blocked in BLACKLISTED_DOMAINS)


def is_automotive_url(url):
    return any(keyword in url.lower() for keyword in AUTOMOTIVE_KEYWORDS)

if not os.path.exists (DATA_DIR) :
    os.makedirs(DATA_DIR)

#gets the page to use 
def fetch_page(url):
    print(f"Crawling: {url}")
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
        skip_patterns = [
            '/media/', '/careers/', '/contact', 
            'facebook.com', 'twitter.com', 
            '.pdf', '.jpg', '.png', 
            'quotes.toscrape.com',
            '/comments', '/tags', '/page/'
        ]
        if any(pattern in href.lower() for pattern in skip_patterns):
            continue
        if not href or href.startswith('#') or href.startswith('javascript:'):
            continue 
        full_url = urljoin(current_url, href)
        full_url = full_url.rstrip('/')
        if (is_valid_domain(full_url) and 
            allowed_domain in full_url):
            links.add(full_url)
    
    return links

def is_valid_content(html):
    content = BeautifulSoup(html, 'html.parser').get_text()

    word_count = sum(content.lower().count(word) for word in AUTOMOTIVE_KEYWORDS)
    return word_count > 2 

def save_text(url, html, doc_id):
    if not is_valid_content(html):
        return False
    soup = BeautifulSoup(html, 'html.parser')
    for scirpt in soup(["script", "style", "nav", "footer", "header"]):
        scirpt.decompose()
    main_content = soup.find(['article', 'main', 'div'],class_=re.compile('(content|article|body)'))
    if main_content:
        text = main_content.get_text(separator=' ', strip=True)
    else:
        text = soup.get_text(separator=' ', strip=True)
    #skip page
    if len(text.split()) < 50:
        return False
    
    filename = os.path.join(DATA_DIR, f"doc_{doc_id}.txt")
    with open(filename,'w', encoding='utf-8') as f:
        f.write(url + "\n\n" + text)
    print(f"Saved: doc_{doc_id}.txt")
    return True


def crawl(start_url, allowed_domain):
    queue = [start_url]
    visited = set()
    depth = {start_url: 0}
    count = 0
    while queue and count < MAX_PAGES :
        url = queue.pop(0)
        current_depth = depth.get(url, 0)
        if current_depth >= MAX_DEPTH:
            continue

        if url in visited:
            continue 
        visited.add(url)
        html = fetch_page(url)
        if html is not None:
            saved = save_text(url, html, count)  # Check if saved
            if saved:
                count += 1
            new_links = parse_links(html, url, allowed_domain)
            for link in new_links:
                if link not in visited and link not in queue:
                    queue.append(link)
                    depth[link] = current_depth + 1
        time.sleep(CRAWL_DELAY)


if __name__ == "__main__":
    print(f" Starting Automotive Search Engine Crawler")
    print(f" Total seed URLs: {len(SEED_URLS)}")
    print(f" Max pages per domain: {MAX_PAGES}")
    print("=" * 50)
    
    total_docs_saved = 0
    
    for i, seed_url in enumerate(SEED_URLS, 1):
        print(f"\n[{i}/{len(SEED_URLS)}] Crawling {seed_url}")
        print("-" * 50)
        
        domain = urlparse(seed_url).netloc
        
        try:
            crawl(seed_url, domain)
        except Exception as e:
            print(f"❌ Error crawling {seed_url}: {e}")
            continue
    
    # Count total documents
    total_docs = len([f for f in os.listdir(DATA_DIR) if f.endswith('.txt')])
    print("\n" + "=" * 50)
    print(f"Crawling complete!")