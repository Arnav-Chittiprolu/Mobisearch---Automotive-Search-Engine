# vertical-search-engine
# 🏎️ MobiSearch - Automotive Search Engine

**MobiSearch** is a specialized search engine built from scratch for the automotive industry. It crawls, indexes, and ranks documents related to electric vehicles, engine technology, and automotive news using TF-IDF (Term Frequency-Inverse Document Frequency) algorithms.

## 🚀 Features

* **Custom Web Crawler:** Automatically scrapes content from major automotive websites (Tesla, Ford, etc.).
* **TF-IDF Ranking:** Ranks search results by relevance, not just keyword matching.
* **Inverted Index:** Efficiently maps thousands of keywords to documents for fast retrieval.
* **Modern UI:** A clean, dark-mode interface built with **Flask** and **Tailwind CSS**.
* **Pagination:** Handles large result sets with a user-friendly navigation system.

## 🛠️ Tech Stack

* **Language:** Python 3.9+
* **Web Framework:** Flask
* **Frontend:** HTML5, Jinja2, Tailwind CSS
* **Data Processing:** NLTK / Custom Tokenizer
* **Libraries:** `requests`, `beautifulsoup4`, `flask`

## 📂 Project Structure

```text
mobi-search/
├── data/                 # Crawled text documents (.txt)
├── templates/            # HTML files
│   ├── index.html        # Search Home (Hero Page)
│   └── results.html      # Search Results Page
├── app.py                # Main Flask application
├── crawler.py            # Web crawler logic
├── indexer.py            # TF-IDF algorithm and Index builder
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation

⚙️ Installation & Setup
Clone the repository

Bash

git clone [https://github.com/yourusername/mobisearch.git](https://github.com/yourusername/mobisearch.git)
cd mobisearch
Create a Virtual Environment

Bash

python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
Install Dependencies

Bash

pip install -r requirements.txt
🏃‍♂️ How to Run
1. Start the Search Engine
The application will automatically load existing documents from the data/ folder and build the index in memory.

Bash

python3 app.py
Open your browser and go to: http://127.0.0.1:5000

2. (Optional) Run the Crawler
If you want to fetch fresh data, run the crawler script. Note: This may take several minutes.

Bash

python3 crawler.py
🧠 How It Works
Crawling: The crawler.py script visits seed URLs (defined in the code), downloads the HTML, cleans it, and saves the text content to the data/ directory.

Indexing: On startup, indexer.py reads all documents, tokenizes the text (removes stopwords like "the", "and"), and builds an Inverted Index.

Ranking: When a user searches for "electric battery":

The engine calculates the TF-IDF score for that query against every document.

TF (Term Frequency): How often "battery" appears in a specific doc.

IDF (Inverse Document Frequency): How rare "battery" is across all docs (gives more weight to unique words).

Display: Results are sorted by score and displayed via Flask/Jinja template