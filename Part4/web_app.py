import httpagentparser  # for getting the user agent as JSON
import os
import uuid
from flask import Flask, render_template, session, request
from myapp.search.search_engine import SearchEngine
from myapp.search.load_corpus import load_corpus
from json import JSONEncoder
import json

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
                print(f"Skipping invalid JSON entry on line {line_number}: {line.strip()}")
    return valid_entries

DATA = load_valid_json('./static/farmers-protest-tweets.json')

# Instantiate search engine
search_engine = SearchEngine(corpus=corpus, data=DATA)

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

@app.route('/search', methods=['POST'])
def search_form_post():
    search_query = request.form['search-query']
    session['last_search_query'] = search_query

    search_id = str(uuid.uuid4())  # Generate a unique identifier
    results = search_engine.search(search_query, search_id)

    if results:
        found_count = len(results)
        session['last_found_count'] = found_count
    else: pass # TODO: empty results

    print(session)
    return render_template('results.html', query=search_query, results_list=results, page_title="Results", found_counter=found_count)

if __name__ == "__main__":
    app.run(port=8088, host="0.0.0.0", threaded=False, debug=True)
