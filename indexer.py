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
    
    results = results[:50]
    return results

if __name__ == "__main__":
    print("\n🚀 STARTING INDEXER DIAGNOSTIC...")
    
    # 1. Test Loading
    print("   Loading documents...", end=" ")
    docs = load_documents()
    print(f"✅ Done. ({len(docs)} documents loaded)")

    # 2. Test Indexing
    print("   Building index...", end=" ")
    index = build_inverted_index(docs)
    print(f"✅ Done. ({len(index)} unique terms mapped)")

    # 3. Test Search
    test_q = "electric"
    print(f"\n🔍 Testing search for query: '{test_q}'")
    results = search(test_q, docs, index)
    
    if results:
        print(f"   ✅ Success! Found {len(results)} matches.")
        print(f"   🏆 Top Result: {results[0]['url']} (Score: {results[0]['score']})")
    else:
        print("   ⚠️ No results found. Check your crawler data.")

    print("\n🏁 DIAGNOSTIC COMPLETE.\n")


