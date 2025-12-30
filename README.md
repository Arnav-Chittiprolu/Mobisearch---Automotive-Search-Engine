# MobiSearch - Automotive Search Engine

**MobiSearch** is a specialized search engine built from scratch for the automotive industry. It crawls, indexes, and ranks documents related to electric vehicles, engine technology, and automotive news using TF-IDF (Term Frequency-Inverse Document Frequency) algorithms.

## Features

* **Custom Web Crawler:** Automatically scrapes content from major automotive websites.
* **TF-IDF Ranking:** Ranks search results by relevance, not just keyword matching.
* **Inverted Index:** Efficiently maps thousands of keywords to documents for fast retrieval.
* **Modern UI:** A clean, dark-mode interface built with **Flask** and **Tailwind CSS**.
* **Pagination:** Handles large result sets with a user-friendly navigation system.

## Tech Stack

* **Language:** Python 3.9+
* **Web Framework:** Flask
* **Frontend:** HTML5, Jinja2, Tailwind CSS
* **Data Processing:** NLTK / Custom Tokenizer
* **Libraries:** `requests`, `beautifulsoup4`, `flask`

## Installation & Setup

* **Clone:** `git clone https://github.com/yourusername/mobisearch.git`
* **Directory:** `cd mobisearch`
* **Environment:** `python3 -m venv venv`
* **Activate:** `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
* **Install:** `pip install -r requirements.txt`

## How to Run

* **Crawl Data:** Run `python3 crawler.py` to fetch new documents (Will take some time).
* **Start App:** Run `python3 app.py` and open `http://127.0.0.1:5001`

## How It Works

* **Crawling:** Visits seed URLs, downloads HTML, cleans it, and saves text to `data/`.
* **Indexing:** Reads documents, removes stopwords, and builds an **Inverted Index** on startup.
* **Ranking:** Calculates **TF-IDF** scores (Term Frequency-Inverse Document Frequency) to rank results.
* **Display:** Renders sorted results via Flask/Jinja templates with a Tailwind CSS frontend.

## Project Structure

```text
mobi-search/
├── data/                 # Generated locally after running crawler.py
├── templates/            # HTML files
├── app.py                # Main Flask application
├── crawler.py            # Web crawler logic
├── indexer.py            # TF-IDF algorithm and Index builder
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
