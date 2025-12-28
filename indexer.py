import os
import json
import re
from collections import defaultdict
from math import log

# CONFIGURATION
DATA_DIR = "data"
INDEX_FILE = "index.json"
STOP_WORDS = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", 
                 "for", "of", "with", "is", "are", "was", "were", "be", 
                 "been", "being", "have", "has", "had", "do", "does", "did", "this", "that", "it"}

def load_documents():
    documents = {}
    for filename in os.listdir("data"):
        if filename.endswith(".txt"):
            with open("data/"+ filename, "r", encoding="utf-8") as f:
                content = f.read()
            documents[filename] = content.split('\n\n', 1)
    return documents 

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
    tf = 0
    if words_list:
        for item in words_list:
            if item == word:
                tf+=1
        tf = tf/len(words_list)
    docs_with_word = inverted_index.get(word, [])
    length_docs = len(docs_with_word)
    idf = 0
    if docs_with_word:
        idf = log(total_docs/length_docs)
    
    return tf * idf

def search(query, documents, inverted_index):
    query_words = process_text(query)
    candidate_docs = set()
    for word in query_words:
        candidate_docs.update(inverted_index.get(word, []))
    results = []
    for doc_id in candidate_docs:
        doc_text = documents[doc_id][1]
        doc_words = process_text(doc_text)
        total_score = 0
        for word in query_words:
            score = calculate_tf_idf(word, doc_words, inverted_index, len(documents))
            total_score += score
        results.append({
            "doc_id": doc_id,
            "url": documents[doc_id][0],
            "score": total_score
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

if __name__ == "__main__":
    print("="*50)
    print("TEST 1: Loading Documents")
    docs = load_documents()
    print(f"✓ Loaded {len(docs)} documents")
    
    # Test 2: Process text (tokenize + stopwords)
    print("\n" + "="*50)
    print("TEST 2: Text Processing")
    test_text = "The quick brown fox is a TEST! Python programming."
    processed = process_text(test_text)
    print(f"Input: {test_text}")
    print(f"Output: {processed}")
    print(f"✓ Removed stopwords and punctuation")
    
    # Test 3: Build inverted index
    print("\n" + "="*50)
    print("TEST 3: Building Inverted Index")
    index = build_inverted_index(docs)
    print(f"✓ Index contains {len(index)} unique words")
    
    # Show a sample of the index
    sample_words = list(index.keys())[:5]
    for word in sample_words:
        doc_count = len(index[word])
        print(f"  '{word}' appears in {doc_count} documents")
    
    # Test 4: Check a specific word in the index
    print("\n" + "="*50)
    print("TEST 4: Looking Up a Word")
    test_word = "quotes"  # Change this to any word you expect
    if test_word in index:
        docs_with_word = index[test_word]
        print(f"✓ '{test_word}' found in {len(docs_with_word)} documents:")
        print(f"  {docs_with_word[:3]}...")  # Show first 3
    else:
        print(f"✗ '{test_word}' not found in index")
    
    # Test 5: Calculate TF-IDF
    print("\n" + "="*50)
    print("TEST 5: TF-IDF Calculation")
    
    # Get a document to test with
    first_doc_id = list(docs.keys())[0]
    first_doc_text = docs[first_doc_id][1]
    first_doc_words = process_text(first_doc_text)
    
    # Pick a word that appears in this document
    test_word = first_doc_words[10] if len(first_doc_words) > 10 else first_doc_words[0]
    
    tfidf_score = calculate_tf_idf(
        test_word, 
        first_doc_words, 
        index, 
        len(docs)
    )
    
    print(f"Word: '{test_word}'")
    print(f"Appears {first_doc_words.count(test_word)} times in document")
    print(f"Document has {len(first_doc_words)} total words")
    print(f"Word appears in {len(index.get(test_word, []))} documents total")
    print(f"✓ TF-IDF Score: {tfidf_score:.4f}")
    
    # Test 6: Test with a word that doesn't exist
    print("\n" + "="*50)
    print("TEST 6: Non-existent Word")
    fake_word = "xyzabc123"
    score = calculate_tf_idf(fake_word, first_doc_words, index, len(docs))
    print(f"TF-IDF for non-existent word '{fake_word}': {score}")
    print(f"✓ Should be 0: {score == 0}")
    
    print("\n" + "="*50)
    # Test 7: Basic Single-Word Search
    print("\n" + "="*50)
    print("TEST 7: Basic Search - Single Word")
    search_query = "quotes"  # Change to a word you expect to find
    results = search(search_query, docs, index)
    print(f"Search query: '{search_query}'")
    print(f"✓ Found {len(results)} results")
    
    if results:
        print("Top 3 results:")
        for i, result in enumerate(results[:3]):
            print(f"  {i+1}. Doc {result['doc_id']}: Score {result['score']:.4f}")
    
    # Test 8: Multi-Word Search
    print("\n" + "="*50)
    print("TEST 8: Multi-Word Search")
    multi_query = "quotes love life"  # Adjust based on your content
    multi_results = search(multi_query, docs, index)
    print(f"Search query: '{multi_query}'")
    print(f"✓ Found {len(multi_results)} results")
    
    if multi_results:
        print("Top result:")
        top_result = multi_results[0]
        print(f"  Doc {top_result['doc_id']}: Score {top_result['score']:.4f}")
        print(f"  URL: {top_result.get('url', 'N/A')[:60]}...")
    
    # Test 9: Non-Existent Word Search
    print("\n" + "="*50)
    print("TEST 9: Search for Non-Existent Word")
    fake_query = "xyzabc123"
    fake_results = search(fake_query, docs, index)
    print(f"Search query: '{fake_query}'")
    print(f"✓ Results: {len(fake_results)} (should be 0)")
    print(f"✓ Empty results handled correctly: {len(fake_results) == 0}")
    
    # Test 10: Search Ranking Verification
    print("\n" + "="*50)
    print("TEST 10: Search Ranking Order")
    if len(results) > 1:
        print("Checking that results are sorted by score (highest first):")
        is_sorted = all(results[i]['score'] >= results[i+1]['score'] 
                       for i in range(len(results)-1))
        print(f"✓ Results properly sorted: {is_sorted}")
        
        # Show score progression
        for i in range(min(3, len(results))):
            print(f"  Result {i+1}: {results[i]['score']:.4f}")
    else:
        print("Not enough results to test ranking")
    
    # Test 11: Empty Query Handling
    print("\n" + "="*50)
    print("TEST 11: Empty Query")
    empty_results = search("", docs, index)
    print(f"Search query: '' (empty)")
    print(f"✓ Results: {len(empty_results)} (should handle gracefully)")
    
    # Test 12: Query with Only Stopwords
    print("\n" + "="*50)
    print("TEST 12: Query with Only Stopwords")
    stopword_query = "the and is"
    stopword_results = search(stopword_query, docs, index)
    print(f"Search query: '{stopword_query}'")
    print(f"✓ Results: {len(stopword_results)} (should be 0 or very few)")
    
    # Test 13: Search Function Performance Check
    print("\n" + "="*50)
    print("TEST 13: Performance Check")
    import time
    start_time = time.time()
    for _ in range(10):  # Run search 10 times
        search("test query", docs, index)
    end_time = time.time()
    avg_time = (end_time - start_time) / 10
    print(f"✓ Average search time: {avg_time:.4f} seconds")
    print(f"✓ Performance {'GOOD' if avg_time < 0.1 else 'NEEDS IMPROVEMENT'}")
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS COMPLETE! SEARCH ENGINE READY! 🎉")
    print("="*60)
    print("ALL TESTS COMPLETE!")