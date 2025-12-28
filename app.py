from flask import Flask, render_template, request
from indexer import load_documents, build_inverted_index, search


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

docs = load_documents()
index = build_inverted_index(docs)

@app.route("/search")
def search_page():
    query = request.args.get("q")
    results = search(query, docs, index)
    return render_template("results.html", query=query, results=results)

if __name__ == "__main__":
    app.run(debug=True)