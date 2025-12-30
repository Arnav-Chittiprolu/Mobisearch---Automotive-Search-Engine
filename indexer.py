import os
import re
from collections import defaultdict
from math import log

# CONFIGURATION
DATA_DIR = "data"
INDEX_FILE = "index.json"
STOP_WORDS = {
    # Articles
    "the", "a", "an",
    
    # Conjunctions
    "and", "or", "but", "if", "because",
    
    # Prepositions
    "in", "on", "at", "to", "for", "of", "with", "by", "from",
    "about", "into", "through", "during", "before", "after",
    "above", "below", "between", "under",
    
    # Be verbs
    "is", "are", "was", "were", "be", "been", "being",
    
    # Have verbs
    "have", "has", "had",
    
    # Do verbs
    "do", "does", "did",
    
    # Pronouns
    "i", "you", "he", "she", "it", "we", "they",
    "this", "that", "these", "those",
    "my", "your", "his", "her", "its", "our", "their",
    
    # Common words
    "will", "would", "could", "should", "can", "may", "might",
    "just", "also", "very", "really", "only", "even",
    "more", "most", "other", "some", "any", "all", "each",
    "no", "not", "so", "than", "too", "now", "here", "there"
}

# DO NOT include: car, vehicle, electric, battery, engine, motor, etc.
# These are words you WANT to find!
AUTOMOTIVE_KEYWORDS = [
    'electric', 'vehicle', 'car', 'battery', 
    'automobile', 'automotive', 'ev', 'tesla', 
    'ford', 'gm', 'toyota', 'nissan', 'charging',
    'motor', 'engineering', 'technology'
]
BLOCKED_DOMAINS = ['quotes.toscrape.com', 'toscrape.com']


def load_documents():
    documents = {}
    for filename in os.listdir("data"):
        if filename.endswith(".txt"):
            filepath = os.path.join(DATA_DIR, filename)
            with open("data/"+ filename, "r", encoding="utf-8") as f:
                content = f.read()
            parts = content.split('\n\n', 1)
            if any(domain in parts[0] for domain in BLOCKED_DOMAINS):
                continue
            if len(parts) == 2 and is_valid_automotive_content(parts[1]):
                documents[filename.replace('.txt', '')] = parts
    return documents 

def is_valid_automotive_content(text):
    text_lower = text.lower()
    keyword_count = sum(text_lower.count(keyword) for keyword in AUTOMOTIVE_KEYWORDS)
    return keyword_count >= 5

def process_text(text):
    lower = text.lower()
    words = re.findall(r'[a-z]+', lower)
    result = []
    for word in words:
        if word not in STOP_WORDS:
            result.append(word)
    return result

def build_inverted_index(documents):
    index = defaultdict(list)
    for doc_id, content in documents.items():
        text = content[1]
        words = process_text(text)
        unique_words = set(words)
        for word in unique_words:
            index[word].append(doc_id)
    return index

def calculate_tf_idf(word, words_list, inverted_index, total_docs):
    tf = words_list.count(word) / len(words_list) if words_list else 0
    
    docs_with_word = inverted_index.get(word, [])
    idf = log(total_docs / (len(docs_with_word) + 1))  
    
    return tf * idf

def search(query, documents, inverted_index):
    query_words = process_text(query)
    candidate_docs = set()

    for word in query_words:
        candidate_docs.update(inverted_index.get(word, []))
    
    # More flexible matching
    results = []
    for doc_id, doc_content in documents.items():
        url = documents[doc_id][0]
        
        # Skip results from blocked domains
        if any(domain in url for domain in BLOCKED_DOMAINS):
            continue

        doc_text = documents[doc_id][1]
        doc_words = process_text(doc_content[1])
        total_score = 0
        
        for word in query_words:
            score = calculate_tf_idf(word, doc_words, inverted_index, len(documents))
            total_score += score
        
        if total_score >= 0.001:
            results.append({
                 "doc_id": doc_id,
                  "url": doc_content[0],
                 "score": total_score
            })
    results.sort(key=lambda x: x["score"], reverse=True)

    if results:
        max_score = results[0]["score"]
        if max_score > 0:
            for result in results:
                # Convert to percentage, round to integer
                result["score"] = round((result["score"] / max_score) * 100)
        # Sort by best matches
    return results


def debug_search_engine(docs, index, query):
    print("\n" + "="*50)
    print(f"🔍 Debugging Search for Query: '{query}'")
    print("="*50)

    # 1. Tokenization Check
    print("\n📝 TOKENIZATION CHECK:")
    processed_query = process_text(query)
    print(f"Raw Query: '{query}'")
    print(f"Processed Query Words: {processed_query}")

    # 2. Document Content Analysis
    print("\n📄 DOCUMENT ANALYSIS:")
    print(f"Total Documents: {len(docs)}")
    
    # Sample document content preview
    print("\nDocument Sample Contents:")
    for i, (doc_id, content) in enumerate(list(docs.items())[:3], 1):
        print(f"\nDocument {i} (ID: {doc_id}):")
        print(f"URL: {content[0]}")
        print(f"Preview: {content[1][:100]}...")

    # 3. Index Coverage
    print("\n🔢 INDEX COVERAGE:")
    for word in processed_query:
        docs_with_word = index.get(word, [])
        print(f"Word '{word}': {len(docs_with_word)} documents")
        if docs_with_word:
            print(f"  First 3 documents: {docs_with_word[:3]}")

    # 4. Stopword Diagnostic
    print("\n🚫 STOPWORD DIAGNOSTIC:")
    print("Current Stopwords:")
    for word in processed_query:
        is_stopword = word in STOP_WORDS
        print(f"  '{word}': {'STOPWORD ⚠️' if is_stopword else 'OK ✅'}")

    # 5. Detailed Search Attempt
    print("\n🕵️ DETAILED SEARCH ATTEMPT:")
    try:
        results = search(query, docs, index)
        print(f"Total Results: {len(results)}")
        
        if results:
            print("\nTop Results:")
            for i, result in enumerate(results[:3], 1):
                print(f"\nResult {i}:")
                print(f"  Document ID: {result['doc_id']}")
                print(f"  URL: {result['url']}")
                print(f"  Score: {result['score']}")
                print(f"  Text Preview: {result['text'][:100]}...")
        else:
            print("No results found.")
    except Exception as e:
        print(f"Error during search: {e}")

    # 6. Potential Index Issues
    print("\n🔍 POTENTIAL INDEX ISSUES:")
    index_word_counts = {word: len(docs) for word, docs in index.items()}
    sorted_words = sorted(index_word_counts.items(), key=lambda x: x[1])
    
    print("Least Common Words:")
    for word, count in sorted_words[:5]:
        print(f"  '{word}': {count} documents")

    # 7. Comprehensive Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if len(docs) < 50:
        print("⚠️ Low document count. Re-run crawler with more sources.")
    
    if not processed_query:
        print("⚠️ Query not processing correctly. Check tokenization.")
    
    if len(index) < 100:
        print("⚠️ Very small index. Verify crawler and indexing process.")


if __name__ == "__main__":
    test_queries = ['car', 'automobile', 'vehicle', 'electric', 'battery']
    docs = load_documents()
    for query in test_queries:
        debug_search_engine(docs, build_inverted_index(docs), query)
    print("="*50)
print("DOCUMENT DIAGNOSTIC")
print("="*50)

# Count documents
files = [f for f in os.listdir(DATA_DIR) if f.endswith('.txt')]
print(f"\nTotal documents: {len(files)}")

# Check each document
for filename in files[:10]:  # First 10
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    parts = content.split('\n\n', 1)
    url = parts[0]
    text = parts[1] if len(parts) > 1 else ""
    
    print(f"\n📄 {filename}")
    print(f"   URL: {url}")
    print(f"   Text length: {len(text)} characters")
    print(f"   Word count: {len(text.split())}")
    print(f"   Preview: {text[:100]}...")
    
    # Check for automotive keywords
    keywords = ['car', 'electric', 'vehicle', 'battery', 'automotive']
    found = [k for k in keywords if k in text.lower()]
    print(f"   Automotive keywords found: {found}")
