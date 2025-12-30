import requests
from bs4 import BeautifulSoup
import time
import os
import re
from urllib.parse import urljoin, urlparse
import hashlib


doc_counter = 0
seen_urls = set()
seen_hashes = set()

MAX_PAGES = 20
MAX_DEPTH = 2
CRAWL_DELAY = 0.0001
DATA_DIR = "data"
url_log_file = os.path.join(DATA_DIR, "crawled_urls.txt")
hash_log_file = os.path.join(DATA_DIR, "content_hashes.txt")

SEED_URLS = [
    "https://www.caranddriver.com/news/",
    "https://www.motortrend.com/news/",
    "https://www.autoweek.com/news/",
    "https://www.thedrive.com/news/",
    "https://en.wikipedia.org/wiki/Electric_vehicle",
    "https://en.wikipedia.org/wiki/Electric_car",
    "https://en.wikipedia.org/wiki/Battery_electric_vehicle",
    "https://en.wikipedia.org/wiki/Plug-in_hybrid",
    "https://en.wikipedia.org/wiki/Hybrid_vehicle",
    "https://en.wikipedia.org/wiki/Hydrogen_vehicle",
    "https://en.wikipedia.org/wiki/Fuel_cell_vehicle",
    
    # Battery Technology
    "https://en.wikipedia.org/wiki/Electric_battery",
    "https://en.wikipedia.org/wiki/Lithium-ion_battery",
    "https://en.wikipedia.org/wiki/Solid-state_battery",
    "https://en.wikipedia.org/wiki/Battery_electric_vehicle#Battery_technology",
    "https://en.wikipedia.org/wiki/EV_battery",
    
    # Major Manufacturers
    "https://en.wikipedia.org/wiki/Tesla,_Inc.",
    "https://en.wikipedia.org/wiki/Ford_Motor_Company",
    "https://en.wikipedia.org/wiki/General_Motors",
    "https://en.wikipedia.org/wiki/Toyota",
    "https://en.wikipedia.org/wiki/Honda",
    "https://en.wikipedia.org/wiki/Nissan",
    "https://en.wikipedia.org/wiki/Volkswagen",
    "https://en.wikipedia.org/wiki/BMW",
    "https://en.wikipedia.org/wiki/Mercedes-Benz",
    "https://en.wikipedia.org/wiki/Audi",
    "https://en.wikipedia.org/wiki/Porsche",
    "https://en.wikipedia.org/wiki/Hyundai",
    "https://en.wikipedia.org/wiki/Kia_Motors",
    "https://en.wikipedia.org/wiki/Chevrolet",
    "https://en.wikipedia.org/wiki/GMC_(automobile)",
    "https://en.wikipedia.org/wiki/Cadillac",
    "https://en.wikipedia.org/wiki/Ram_Trucks",
    "https://en.wikipedia.org/wiki/Lincoln_(automobile)",
    "https://en.wikipedia.org/wiki/Lexus",
    "https://en.wikipedia.org/wiki/Subaru",
    "https://en.wikipedia.org/wiki/Mazda",
    "https://en.wikipedia.org/wiki/Mitsubishi_Motors",
    "https://en.wikipedia.org/wiki/Daimler_AG",
    "https://en.wikipedia.org/wiki/Volvo_Cars",
    "https://en.wikipedia.org/wiki/Polestar",
    "https://en.wikipedia.org/wiki/Rivian",
    "https://en.wikipedia.org/wiki/Lucid_Motors",
    "https://en.wikipedia.org/wiki/BYD_Company",
    "https://en.wikipedia.org/wiki/NIO_(company)",
    "https://en.wikipedia.org/wiki/Xpeng",
    "https://en.wikipedia.org/wiki/Li_Auto",
    
    # Specific Car Models (EVs)
    "https://en.wikipedia.org/wiki/Tesla_Model_S",
    "https://en.wikipedia.org/wiki/Tesla_Model_3",
    "https://en.wikipedia.org/wiki/Tesla_Model_X",
    "https://en.wikipedia.org/wiki/Tesla_Model_Y",
    "https://en.wikipedia.org/wiki/Tesla_Roadster",
    "https://en.wikipedia.org/wiki/Nissan_Leaf",
    "https://en.wikipedia.org/wiki/Chevrolet_Bolt",
    "https://en.wikipedia.org/wiki/Ford_Mustang_Mach-E",
    "https://en.wikipedia.org/wiki/Ford_F-150_Lightning",
    "https://en.wikipedia.org/wiki/Volkswagen_ID.4",
    "https://en.wikipedia.org/wiki/Volkswagen_ID.5",
    "https://en.wikipedia.org/wiki/Audi_e-tron",
    "https://en.wikipedia.org/wiki/BMW_i3",
    "https://en.wikipedia.org/wiki/BMW_i4",
    "https://en.wikipedia.org/wiki/BMW_iX",
    "https://en.wikipedia.org/wiki/Mercedes-Benz_EQC",
    "https://en.wikipedia.org/wiki/Hyundai_Ioniq",
    "https://en.wikipedia.org/wiki/Hyundai_Kona_Electric",
    "https://en.wikipedia.org/wiki/Kia_EV6",
    "https://en.wikipedia.org/wiki/Kia_Niro_EV",
    "https://en.wikipedia.org/wiki/Lucid_Air",
    "https://en.wikipedia.org/wiki/Rivian_R1T",
    "https://en.wikipedia.org/wiki/Rivian_R1S",
    
    # Automotive Technology
    "https://en.wikipedia.org/wiki/Automotive_industry",
    "https://en.wikipedia.org/wiki/Car",
    "https://en.wikipedia.org/wiki/Automobile",
    "https://en.wikipedia.org/wiki/Internal_combustion_engine",
    "https://en.wikipedia.org/wiki/Electric_motor",# Advanced Automotive Technologies
    "https://en.wikipedia.org/wiki/Autonomous_car",
    "https://en.wikipedia.org/wiki/Self-driving_car",
    "https://en.wikipedia.org/wiki/Advanced_driver-assistance_systems",
    "https://en.wikipedia.org/wiki/Vehicle-to-grid",
    "https://en.wikipedia.org/wiki/Charging_station",
    "https://en.wikipedia.org/wiki/Regenerative_brake",
    "https://en.wikipedia.org/wiki/Electric_vehicle_battery",
    "https://en.wikipedia.org/wiki/Battery_management_system",
    "https://en.wikipedia.org/wiki/Electric_vehicle_charging_network",
    "https://en.wikipedia.org/wiki/Fast-charging",
    
    # Automotive Engineering & Design
    "https://en.wikipedia.org/wiki/Automotive_engineering",
    "https://en.wikipedia.org/wiki/Vehicle_dynamics",
    "https://en.wikipedia.org/wiki/Suspension_(vehicle)",
    "https://en.wikipedia.org/wiki/Transmission_(mechanics)",
    "https://en.wikipedia.org/wiki/Drivetrain",
    "https://en.wikipedia.org/wiki/All-wheel_drive",
    "https://en.wikipedia.org/wiki/Four-wheel_drive",
    "https://en.wikipedia.org/wiki/Aerodynamics",
    "https://en.wikipedia.org/wiki/Automotive_design",
    "https://en.wikipedia.org/wiki/Car_platform",
    
    # Emerging Manufacturers & Startups
    "https://en.wikipedia.org/wiki/Fisker_Inc.",
    "https://en.wikipedia.org/wiki/Canoo",
    "https://en.wikipedia.org/wiki/Lordstown_Motors",
    "https://en.wikipedia.org/wiki/Arrival_(company)",
    "https://en.wikipedia.org/wiki/Faraday_Future",
    "https://en.wikipedia.org/wiki/Byton",
    "https://en.wikipedia.org/wiki/VinFast",
    "https://en.wikipedia.org/wiki/Ola_Electric",
    
    # Chinese EV Manufacturers
    "https://en.wikipedia.org/wiki/BYD_Auto",
    "https://en.wikipedia.org/wiki/Geely",
    "https://en.wikipedia.org/wiki/Great_Wall_Motors",
    "https://en.wikipedia.org/wiki/SAIC_Motor",
    "https://en.wikipedia.org/wiki/WM_Motor",
    "https://en.wikipedia.org/wiki/Human_Horizons",
    
    # Specific EV Models (Not Listed)
    "https://en.wikipedia.org/wiki/Porsche_Taycan",
    "https://en.wikipedia.org/wiki/Audi_Q4_e-tron",
    "https://en.wikipedia.org/wiki/Polestar_2",
    "https://en.wikipedia.org/wiki/Volvo_XC40_Recharge",
    "https://en.wikipedia.org/wiki/Mazda_MX-30",
    "https://en.wikipedia.org/wiki/Jaguar_I-Pace",
    "https://en.wikipedia.org/wiki/Genesis_GV60",
    "https://en.wikipedia.org/wiki/GMC_Hummer_EV",
    "https://en.wikipedia.org/wiki/Cadillac_Lyriq",
    
    # Battery & Energy Storage
    "https://en.wikipedia.org/wiki/Nickel-metal_hydride_battery",
    "https://en.wikipedia.org/wiki/Lithium_polymer_battery",
    "https://en.wikipedia.org/wiki/Battery_pack",
    "https://en.wikipedia.org/wiki/Lithium_iron_phosphate_battery",
    "https://en.wikipedia.org/wiki/Energy_density",
    "https://en.wikipedia.org/wiki/Battery_recycling",
    
    # Infrastructure & Charging
    "https://en.wikipedia.org/wiki/Tesla_Supercharger",
    "https://en.wikipedia.org/wiki/CHAdeMO",
    "https://en.wikipedia.org/wiki/Combined_Charging_System",
    "https://en.wikipedia.org/wiki/Electrify_America",
    "https://en.wikipedia.org/wiki/ChargePoint",
    
    # Industry & Market
    "https://en.wikipedia.org/wiki/Electric_car_use_by_country",
    "https://en.wikipedia.org/wiki/Government_incentives_for_plug-in_electric_vehicles",
    "https://en.wikipedia.org/wiki/Electric_vehicle_industry_in_China",
    "https://en.wikipedia.org/wiki/Automotive_industry_in_the_United_States",
    "https://en.wikipedia.org/wiki/Automotive_industry_in_Europe",
    
    # Performance & Racing
    "https://en.wikipedia.org/wiki/Formula_E",
    "https://en.wikipedia.org/wiki/Electric_motorsport",
    "https://en.wikipedia.org/wiki/Extreme_E",
    
    # Alternative Fuels & Technologies
    "https://en.wikipedia.org/wiki/Hydrogen_fuel_cell",
    "https://en.wikipedia.org/wiki/Compressed_natural_gas",
    "https://en.wikipedia.org/wiki/Biodiesel",
    "https://en.wikipedia.org/wiki/Ethanol_fuel",
    "https://en.wikipedia.org/wiki/Alternative_fuel_vehicle",
    
    # Environmental Impact
    "https://en.wikipedia.org/wiki/Environmental_aspects_of_the_electric_car",
    "https://en.wikipedia.org/wiki/Vehicle_emissions",
    "https://en.wikipedia.org/wiki/Zero-emissions_vehicle",    "https://en.wikipedia.org/wiki/Auto_mechanic",
    "https://en.wikipedia.org/wiki/Automobile_repair_shop",
    "https://en.wikipedia.org/wiki/Car_maintenance",
    "https://en.wikipedia.org/wiki/Motor_oil",
    "https://en.wikipedia.org/wiki/Oil_filter",
    "https://en.wikipedia.org/wiki/Air_filter",
    "https://en.wikipedia.org/wiki/Spark_plug",
    "https://en.wikipedia.org/wiki/Car_battery",
    "https://en.wikipedia.org/wiki/Tire",
    "https://en.wikipedia.org/wiki/Tire_rotation",
    "https://en.wikipedia.org/wiki/Wheel_alignment",
    "https://en.wikipedia.org/wiki/Brake_pad",
    "https://en.wikipedia.org/wiki/Disc_brake",
    "https://en.wikipedia.org/wiki/Brake_fluid",
    "https://en.wikipedia.org/wiki/Coolant",
    "https://en.wikipedia.org/wiki/Antifreeze",
    "https://en.wikipedia.org/wiki/Transmission_fluid",
    "https://en.wikipedia.org/wiki/Power_steering",
    "https://en.wikipedia.org/wiki/Windshield_washer_fluid",
    
    # Car Parts & Components
    "https://en.wikipedia.org/wiki/Engine",
    "https://en.wikipedia.org/wiki/Piston",
    "https://en.wikipedia.org/wiki/Crankshaft",
    "https://en.wikipedia.org/wiki/Camshaft",
    "https://en.wikipedia.org/wiki/Cylinder_head",
    "https://en.wikipedia.org/wiki/Gasket",
    "https://en.wikipedia.org/wiki/Timing_belt_(camshaft)",
    "https://en.wikipedia.org/wiki/Serpentine_belt",
    "https://en.wikipedia.org/wiki/Alternator",
    "https://en.wikipedia.org/wiki/Starter_(engine)",
    "https://en.wikipedia.org/wiki/Radiator",
    "https://en.wikipedia.org/wiki/Water_pump",
    "https://en.wikipedia.org/wiki/Thermostat",
    "https://en.wikipedia.org/wiki/Fuel_pump",
    "https://en.wikipedia.org/wiki/Fuel_injector",
    "https://en.wikipedia.org/wiki/Carburetor",
    "https://en.wikipedia.org/wiki/Exhaust_system",
    "https://en.wikipedia.org/wiki/Catalytic_converter",
    "https://en.wikipedia.org/wiki/Muffler",
    "https://en.wikipedia.org/wiki/Shock_absorber",
    "https://en.wikipedia.org/wiki/Strut",
    "https://en.wikipedia.org/wiki/CV_joint",
    "https://en.wikipedia.org/wiki/Drive_shaft",
    "https://en.wikipedia.org/wiki/Differential_(mechanical_device)",
    "https://en.wikipedia.org/wiki/Clutch",
    "https://en.wikipedia.org/wiki/Manual_transmission",
    "https://en.wikipedia.org/wiki/Automatic_transmission",
    "https://en.wikipedia.org/wiki/Continuously_variable_transmission",
    
    # Diagnostic & Tools
    "https://en.wikipedia.org/wiki/On-board_diagnostics",
    "https://en.wikipedia.org/wiki/OBD-II_PIDs",
    "https://en.wikipedia.org/wiki/Check_engine_light",
    "https://en.wikipedia.org/wiki/Automotive_scan_tool",
    "https://en.wikipedia.org/wiki/Multimeter",
    "https://en.wikipedia.org/wiki/Torque_wrench",
    "https://en.wikipedia.org/wiki/Jack_(device)",
    "https://en.wikipedia.org/wiki/Car_jack",
    "https://en.wikipedia.org/wiki/Lug_wrench",
    "https://en.wikipedia.org/wiki/Oil_change",
    
    # Car Systems
    "https://en.wikipedia.org/wiki/Ignition_system",
    "https://en.wikipedia.org/wiki/Fuel_injection",
    "https://en.wikipedia.org/wiki/Engine_control_unit",
    "https://en.wikipedia.org/wiki/Anti-lock_braking_system",
    "https://en.wikipedia.org/wiki/Traction_control_system",
    "https://en.wikipedia.org/wiki/Electronic_stability_control",
    "https://en.wikipedia.org/wiki/Power_window",
    "https://en.wikipedia.org/wiki/Central_locking",
    "https://en.wikipedia.org/wiki/Air_conditioning",
    "https://en.wikipedia.org/wiki/Heating,_ventilation,_and_air_conditioning",
    
    # Car Problems & Troubleshooting
    "https://en.wikipedia.org/wiki/Engine_knocking",
    "https://en.wikipedia.org/wiki/Overheating_(electricity)",
    "https://en.wikipedia.org/wiki/Automobile_handling",
    "https://en.wikipedia.org/wiki/Wheel_balancing",
    "https://en.wikipedia.org/wiki/Automotive_battery#Jump-starting",
    
    # DIY & How-To Resources (from other sites)
    "https://www.wikihow.com/Category:Car-Maintenance-and-Repair",
    "https://mechanics.stackexchange.com/questions",
    
    # Learning About Cars
    "https://en.wikipedia.org/wiki/Automotive_engineering",
    "https://en.wikipedia.org/wiki/Vehicle_identification_number",
    "https://en.wikipedia.org/wiki/Automobile_safety",

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

def load_existing_urls():
    global seen_urls
    if os.path.exists(url_log_file):
        try:
            with open(url_log_file, 'r') as f:
                seen_urls = set(line.strip() for line in f if line.strip())
        except:
            seen_urls = set()
    return seen_urls

def save_crawled_url(url):
    with open(url_log_file, 'a') as f:
        f.write(url + '\n')

def normalize_url(url):
    url = url.split('#')[0]
    url = url.rstrip('/')
    url = url.lower()
    return url

def load_existing_hashes():
    global seen_hashes
    if os.path.exists(hash_log_file):
        try: 
            with open(hash_log_file, 'r') as f:
                seen_hashes = set(line.strip() for line in f if line.strip())
        except:
            seen_hashes = set()
    return seen_hashes

def save_content_hash(content_hash):
    with open(hash_log_file, 'a') as f:
        f.write(content_hash + '\n')

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
    content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    if content_hash in seen_hashes:
        return False
    filename = os.path.join(DATA_DIR, f"doc_{doc_id}.txt")
    with open(filename,'w', encoding='utf-8') as f:
        f.write(url + "\n\n" + text)
    
    seen_hashes.add(content_hash)
    save_content_hash(content_hash)

    print(f"Saved: doc_{doc_id}.txt")
    return True

def get_next_doc_id():
    global doc_counter
    current_id = doc_counter
    doc_counter += 1
    return current_id

def crawl(start_url, allowed_domain):
    queue = [start_url]
    visited = set()
    depth = {start_url: 0}
    local_count = 0

    while queue and local_count < MAX_PAGES :
        url = queue.pop(0)
        normalized = normalize_url(url)
        if normalized in seen_urls:
            continue
        current_depth = depth.get(url, 0)
        if current_depth >= MAX_DEPTH:
            continue

        if url in visited:
            continue 
        visited.add(url)
        seen_urls.add(normalized)
        save_crawled_url(normalized)
        html = fetch_page(url)
        if html is not None:
            doc_id = get_next_doc_id()
            saved = save_text(url, html, doc_id)  # Check if saved
            if saved:
                local_count += 1
            new_links = parse_links(html, url, allowed_domain)
            for link in new_links:
                normalized_link = normalize_url(link)
                if (normalized_link not in seen_urls and 
                link not in visited and link not in queue):
                    queue.append(link)
                    depth[link] = current_depth + 1
        time.sleep(CRAWL_DELAY)

def get_starting_doc_id():
    if not os.path.exists(DATA_DIR):
        return 0
    existing_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.txt')]
    if not existing_files:
        return 0
    max_id = 0
    for filename in existing_files:
        try:
            doc_num = int(filename.replace('doc_', '').replace('.txt', ''))
            max_id = max(max_id, doc_num)
        except:
            continue
    
    return max_id + 1

doc_counter = get_starting_doc_id()

if __name__ == "__main__":
    print(f" Starting Automotive Search Engine Crawler")
    print(f" Total seed URLs: {len(SEED_URLS)}")
    print(f" Max pages per domain: {MAX_PAGES}")
    print("=" * 50)

    # Load existing data
    load_existing_urls()
    load_existing_hashes() 
    print(f"Found {len(seen_urls)} previously crawled URLs")
    print(f"Found {len(seen_hashes)} unique content hashes") 
    
    total_docs_saved = 0
    
    for i, seed_url in enumerate(SEED_URLS, 1):
        print(f"\n[{i}/{len(SEED_URLS)}] Crawling {seed_url}")
        print("-" * 50)
        
        domain = urlparse(seed_url).netloc
        
        try:
            crawl(seed_url, domain)
        except Exception as e:
            print(f"Error crawling {seed_url}: {e}")
            continue
    
    # Count total documents
    total_docs = len([f for f in os.listdir(DATA_DIR) if f.endswith('.txt')])
    print("\n" + "=" * 50)
    print(f"Crawling complete!")
    print(f"Total unique documents: {total_docs}")
    print(f"Total URLs crawled: {len(seen_urls)}")
    print(f"Total unique content hashes: {len(seen_hashes)}")
