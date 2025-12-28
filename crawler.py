import requests
from bs4 import BeautifulSoup
import time
import os
import re
import random
from urllib.parse import urljoin, urlparse

MAX_PAGES = 100
MAX_DEPTH = 3
CRAWL_DELAY = 2
DATA_DIR = "data"
SEED_URLS = [
    "https://www.tesla.com/blog",
    "https://corporate.ford.com//articles/?gnav=footer-aboutford",
     "https://www.energy.gov/eere/vehicles/articles",  # US Department of Energy
    "https://www.batterytechnology.com/",
    "https://www.electrive.com/",
    "https://www.evannex.com/blogs/news",  # Tesla-focused
    "https://www.greentechmedia.com/articles/read/category/electric-vehicles",
    "https://www.insideevs.com/",
     "https://www.gm.com/newsroom.html",
    "https://www.stellantis.com/en/news",
    "https://www.rivian.com/press-releases",
    "https://www.lucidmotors.com/newsroom",
     "https://www.volkswagen-newsroom.com/en",
    "https://www.mercedes-benz.com/en/news/",
    "https://www.bmwusa.com/",
    "https://www.toyota.eu/world/",
    "https://www.peugeot.com/en/news.html",
    "https://www.renault.com/en_global/group/press-releases/",
    "https://www.hyundai.com/worldwide/en/company/pr/list",
    "https://www.nissan-global.com/EN/NEWS/",
    "https://www.kia.com/worldwide/en/company/pr",
    "https://www.sae.org/news/",  # Society of Automotive Engineers
    "https://www.engineering.com/automotive",
    "https://www.automotiveworld.com/",
    "https://www.techrepublic.com/topic/automotive/",
    "https://www.electronicdesign.com/markets/automotive",
    "https://www.assemblymag.com/topics/automotive",
     "https://www.autonews.com/",
    "https://www.motortrend.com/news/",
    "https://www.caranddriver.com/news/",
    "https://www.thedrive.com/",
    "https://www.automotive-news.com/",
    "https://www.jalopnik.com/",
    "https://www.autoweek.com/",
    "https://www.darpa.mil/news-events/transportation",
    "https://www.nhtsa.gov/press-releases",
    "https://www.nrel.gov/transportation/",  # National Renewable Energy Laboratory
    "https://www.ece.cmu.edu/news/transportation",
    "https://www.mit.edu/research/publications/transportation",
]
AUTOMOTIVE_KEYWORDS = [
    'electric vehicle', 'ev battery', 'automotive technology', 
    'car manufacturers', 'vehicle design', 'electric car'
]

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
        skip_patterns = [
            '/media/', '/careers/', '/contact', 
            'facebook.com', 'twitter.com', 
            '.pdf', '.jpg', '.png']
        if any(pattern in href.lower() for pattern in skip_patterns):
            continue
        if not href or href.startswith('#') or href.startswith('javascript:'):
            continue 
        full_url = urljoin(current_url, href)
        full_url = full_url.rstrip('/')
        if allowed_domain in full_url and any(keyword in full_url.lower() 
                                              for keyword in AUTOMOTIVE_KEYWORDS):
            links.add(full_url)
    
    return links

def save_text(url, html, doc_id):
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
    print(f"💾 Saved: doc_{doc_id}.txt")
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
    print(f"🚗 Starting Automotive Search Engine Crawler")
    print(f"📊 Total seed URLs: {len(SEED_URLS)}")
    print(f"📄 Max pages per domain: {MAX_PAGES}")
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
    print(f"✅ Crawling complete!")
    print(f"📚 Total documents saved: {total_docs}")

