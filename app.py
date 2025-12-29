import os
import logging
from flask import Flask, render_template, request
from urllib.parse import urlparse

# Import your modules
from indexer import load_documents, build_inverted_index, search
from crawler import crawl, SEED_URLS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['DATA_DIR'] = 'data'

def initialize_search_engine(force_recrawl=False):
    # Create data directory if it doesn't exist
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    
    # Check if we need to crawl
    if force_recrawl or not os.listdir(app.config['DATA_DIR']):
        logger.info("🕷️ No documents found. Running crawler...")
        
        # Limit to first 5 URLs for quick test
        urls_to_crawl = SEED_URLS[:5]
        
        for url in urls_to_crawl:
            try:
                domain = urlparse(url).netloc
                crawl(url, domain)
            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
    
    # Load documents and build index
    try:
        docs = load_documents()
        index = build_inverted_index(docs)
        
        logger.info(f"📚 Loaded {len(docs)} documents")
        logger.info(f"🔍 Built index with {len(index)} unique words")
        
        return docs, index
    
    except Exception as e:
        logger.error(f"Error initializing search engine: {e}")
        return {}, {}

# Initialize search engine when app starts
docs, index = initialize_search_engine()

@app.route("/")
def home():
    """Home page route"""
    return render_template("index.html")

@app.route("/search")
def search_page():
    """Search results page route"""
    query = request.args.get("q", "")
    
    # Handle empty query
    if not query:
        return render_template("results.html", query=query, results=[])
    
    try:
        results = search(query, docs, index)
        
        # Optional: Add more info to results
        for result in results:
            # Add preview text from document
            result['preview'] = docs[result['doc_id']][1][:200] + "..."
        
        return render_template("results.html", query=query, results=results)
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        return render_template("error.html", message="Search failed. Please try again.")

@app.route("/recrawl")
def recrawl():
    """Force recrawling documents"""
    global docs, index
    docs, index = initialize_search_engine(force_recrawl=True)
    return "Documents recrawled. <a href='/'>Return to home</a>"

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', message="An unexpected error occurred."), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)