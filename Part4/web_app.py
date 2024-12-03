import httpagentparser  # for getting the user agent as JSON
import os
import uuid
from flask import Flask, render_template, session, request
from myapp.search.search_engine import SearchEngine
from myapp.search.load_corpus import load_corpus
from json import JSONEncoder
import json, jsonify
from datetime import datetime

app = Flask(__name__)

# *** Enable using to_json in objects ***
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)

_default.default = JSONEncoder().default
JSONEncoder.default = _default

app.secret_key = 'afgsreg86sr897b6st8b76va8er76fcs6g8d7'
app.session_cookie_name = 'IRWA_SEARCH_ENGINE'

# Load corpus from CSV
full_path = os.path.realpath(__file__)  # Get current path
path, filename = os.path.split(full_path)

file_path = os.path.join(path, "./static/processed_data.csv")  
print(f"File path: {file_path}")

corpus = load_corpus(file_path)
print(f"Loaded corpus. First element: {list(corpus.values())[0]}")

def load_valid_json(file_path):
    valid_entries = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            try:
                json_entry = json.loads(line.strip())
                valid_entries.append(json_entry)
            except json.JSONDecodeError:
                # print(f"Skipping invalid JSON entry on line {line_number}: {line.strip()}")
                pass
    return valid_entries

DATA = load_valid_json('./static/farmers-protest-tweets.json')

# Instantiate search engine
search_engine = SearchEngine(corpus=corpus, data=DATA)

@app.before_request
def track_request():
    # Initialize analytics data in the session if not present
    if 'analytics' not in session:
        session['analytics'] = {
            'requests': [],
            'queries': [],
            'clicks': [],
            'documents': [],
            'user_context': [],
        }
    
    # Log request data
    request_data = {
        "endpoint": request.path,
        "http_method": request.method,
        "timestamp": datetime.now().isoformat(),
        "ip_address": request.remote_addr,
    }
    session['analytics']['requests'].append(request_data)
    # session.modified = True  # Mark session as modified

@app.route('/log_document_click', methods=['POST'])
def log_document_click():
    data = request.json
    document_click_data = {
        "document_id": data.get("document_id"),
        "query_id": data.get("query_id"),
        "rank": data.get("rank"),
        "timestamp": datetime.now().isoformat(),
    }
    session['analytics']['clicks'].append(document_click_data)
    # session.modified = True
    print("HERE ", session['analytics']['clicks'])
    return jsonify({"status": "success"}), 200

# Home URL "/"
@app.route('/')
def index():
    print("Starting home URL /...")

    session['some_var'] = "IRWA 2024 home"
    user_agent = request.headers.get('User-Agent')
    print("Raw user browser:", user_agent)

    user_ip = request.remote_addr
    agent = httpagentparser.detect(user_agent)
    print(f"Remote IP: {user_ip} - JSON user browser {agent}")
    print(session)

    return render_template('index.html', page_title="Welcome")

@app.route('/search', methods=['GET', 'POST'])
def search_form():
    if request.method == 'POST':
        # Handle the search request
        search_query = request.form['search-query']
        session['last_search_query'] = search_query

        search_id = str(uuid.uuid4())  # Generate a unique identifier
        results = search_engine.search(search_query, search_id, top_n=20)

        # Log query analytics
        query_data = {
            "query_id": search_id,
            "query_text": search_query,
            "term_count": len(search_query.split()),
            "timestamp": datetime.now().isoformat(),
            "num_result": len(results)
        }
        session['analytics']['queries'].append(query_data)
        # session.modified = True

        if results:
            found_count = len(results)
            session['last_found_count'] = found_count
            session['search_id'] = search_id  # Save search_id to session for later use
            # Serialize the results for session storage
            session['documents'] = {str(doc.id): doc.__dict__ for doc in results}
        else:
            found_count = 0  # Handle no results scenario
            session['documents'] = {}

        return render_template('results.html', query=search_query, results_list=results, page_title="Results", found_counter=found_count)

    elif request.method == 'GET':
        # Handle fetching results by search_id
        search_id = request.args.get('search_id')  # Retrieve search_id from query parameters
        search_query = session.get('last_search_query', 'No query')
        found_count = session.get('last_found_count', 0)
        results = search_engine.get_results_by_id(search_id)  # Adjust to fetch results by ID

        return render_template('results.html', query=search_query, results_list=results, page_title="Results", found_counter=found_count)

@app.route('/doc_details', methods=['GET'])
def doc_details():
    doc_id = request.args.get("id")
    search_id = request.args.get("search_id") or session.get('search_id')

    # Retrieve the original document from the data source
    original_doc = next((tweet for tweet in DATA if tweet['id'] == int(doc_id)), None)
    document = next((doc for doc in session.get('documents', {}).values() if str(doc['id']) == doc_id), None)

    if doc_id:
        return render_template("doc_details.html", search_id=search_id, doc_id=doc_id, original=original_doc, document=document)
    else:
        return "Document not found", 404

if __name__ == "__main__":
    app.run(port=8088, host="0.0.0.0", threaded=False, debug=True)
