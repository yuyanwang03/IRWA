import httpagentparser  # for getting the user agent as JSON
import os
import uuid
from flask import Flask, render_template, session, request
from myapp.search.search_engine import SearchEngine
from myapp.search.load_corpus import load_corpus
from json import JSONEncoder
import json
from flask import jsonify
from datetime import datetime
import atexit
import requests
from datetime import timedelta
from difflib import SequenceMatcher

# -----------------------------------------------
# Configuration and Constants
# -----------------------------------------------
SESSION_TIMEOUT = timedelta(minutes=60)
SESSION_DIRECTORY = './flask_sessions'
app = Flask(__name__)

app.secret_key = 'afgsreg86sr897b6st8b76va8er76fcs6g8d7'
app.session_cookie_name = 'IRWA_SEARCH_ENGINE'

# -----------------------------------------------
# Utility Functions
# -----------------------------------------------

def _default(self, obj):
    """Enable using to_json in objects."""
    return getattr(obj.__class__, "to_json", _default.default)(obj)

def get_geolocation(ip):
    """Fetch city and country for an IP address using ip-api."""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        if response.status_code == 200:
            data = response.json()
            return data.get("city", "Unknown"), data.get("country", "Unknown")
    except Exception as e:
        print(f"Error fetching geolocation: {e}")
    return "Unknown", "Unknown"

def is_similar(query1, query2, threshold=0.5):
    """Check if two queries are similar using SequenceMatcher."""
    similarity = SequenceMatcher(None, query1, query2).ratio()
    return similarity >= threshold

def load_valid_json(file_path):
    """Load valid JSON entries from a file."""
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

def save_session_to_file():
    """Save session data to a unique file identified by session_id."""
    try:
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())

        analytics = session.get("analytics", {})
        if not any(analytics.get(key, []) for key in ["requests", "queries", "clicks"]):
            return  # Skip saving if analytics is empty

        session['duration'] = (datetime.now() - datetime.fromisoformat(session['user_context']['timestamp'])).total_seconds()

        session_path = os.path.join(SESSION_DIRECTORY, f"{session['session_id']}.json")
        with open(session_path, 'w', encoding='utf-8') as file:
            json.dump(session, file, indent=4)
        print(f"Session data saved to {session_path}")
    except Exception as e:
        print(f"Error saving session data: {e}")

# -----------------------------------------------
# Application Initialization
# -----------------------------------------------

_default.default = JSONEncoder().default
JSONEncoder.default = _default

# Load Corpus and Data
full_path = os.path.realpath(__file__)  # Get current path
path, filename = os.path.split(full_path)
file_path = os.path.join(path, "./static/processed_data.csv")  
corpus = load_corpus(file_path)
DATA = load_valid_json('./static/farmers-protest-tweets.json')

# Instantiate search engine
search_engine = SearchEngine(corpus=corpus, data=DATA)
os.makedirs(SESSION_DIRECTORY, exist_ok=True)

atexit.register(save_session_to_file)

session = {
    'session_id': str(uuid.uuid4()),
    'user_context': None,
    'duration': None,
    'analytics': {
        'requests': [],
        'queries': [],
        'clicks': []
    },
    'last_search_query': None,
    'last_found_count': 0,
    'search_id': None,
    'last_query_documents': {},
    'last_activity': None,
}

# -----------------------------------------------
# Middleware: Tracking and Session Management
# -----------------------------------------------

@app.before_request
def track_physical_session():
    now = datetime.now()
    last_activity = session.get("last_activity")
    
    if last_activity:
        last_activity = datetime.fromisoformat(last_activity)
        if now - last_activity > SESSION_TIMEOUT:
            # Start a new physical session
            session["session_id"] = str(uuid.uuid4())
            session["missions"] = []  # Reset logical missions for new session

    # Update last activity timestamp
    session["last_activity"] = now.isoformat()

    # Ensure session ID exists
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

@app.before_request
def track_request():
    # Log request data
    request_data = {
        "endpoint": request.path,
        "http_method": request.method,
        "timestamp": datetime.now().isoformat(),
        "ip_address": request.remote_addr,
    }
    session['analytics']['requests'].append(request_data)

    if session['user_context'] is None:
        # Get User-Agent and IP information
        user_agent = request.headers.get('User-Agent')
        agent = httpagentparser.detect(user_agent)
        user_ip = request.remote_addr

        # Use GeoIP to get location details (city, country)
        city, country = get_geolocation(user_ip)

        user_context = {
            "browser": agent.get('browser', {}).get('name', 'Unknown'),
            "os": agent.get('os', {}).get('name', 'Unknown'),
            "device": agent.get('dist', {}).get('name', 'Unknown'),
            "ip_address": user_ip,
            "timestamp": datetime.now().isoformat(),
            "time_of_day": datetime.now().strftime("%H:%M:%S"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "city": city,
            "country": country
        }

        session['user_context'] = user_context

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
    return jsonify({"status": "success"}), 200

# -----------------------------------------------
# Routes
# -----------------------------------------------

@app.route('/')
def index():
    """Render the homepage."""
    return render_template('index.html', page_title="Welcome")

@app.route('/search', methods=['GET', 'POST'])
def search_form():
    if request.method == 'POST':
        # Handle the search request
        search_query = request.form['search-query']
        session['last_search_query'] = search_query

        search_id = str(uuid.uuid4())  # Generate a unique identifier
        results = search_engine.search(search_query, search_id, top_n=40)

        # Log query analytics
        query_data = {
            "query_id": search_id,
            "query_text": search_query,
            "term_count": len(search_query.split()),
            "timestamp": datetime.now().isoformat(),
            "num_result": len(results)
        }
        session['analytics']['queries'].append(query_data)

        # Missions: Group queries with the same goal
        missions = session.get("missions", [])

        if missions and is_similar(missions[-1]["queries"][-1]["query_text"], search_query):
            # Add to the current mission
            missions[-1]["queries"].append({
                "query_id": search_id,
                "query_text": search_query,
                "timestamp": datetime.now().isoformat()
            })
        else:
            # Start a new mission
            missions.append({
                "mission_id": str(uuid.uuid4()),
                "queries": [{
                    "query_id": search_id,
                    "query_text": search_query,
                    "timestamp": datetime.now().isoformat()
                }]
            })
        session["missions"] = missions

        if results:
            found_count = len(results)
            session['last_found_count'] = found_count
            session['search_id'] = search_id  # Save search_id to session for later use
            # Serialize the results for session storage
            session['last_query_documents'] = {str(doc.id): doc.__dict__ for doc in results}
        else:
            found_count = 0  # Handle no results scenario
            session['last_query_documents'] = {}

        return render_template('results.html', query=search_query, results_list=results, page_title="Results", found_counter=found_count, search_id=search_id)

    elif request.method == 'GET':
        # Handle fetching results by search_id
        search_id = request.args.get('search_id')  # Retrieve search_id from query parameters
        search_query = session.get('last_search_query', 'No query')
        found_count = session.get('last_found_count', 0)
        results = search_engine.get_results_by_id(search_id)  # Adjust to fetch results by ID

        return render_template('results.html', query=search_query, results_list=results, page_title="Results", found_counter=found_count, search_id=search_id)

@app.route('/doc_details', methods=['GET'])
def doc_details():
    doc_id = request.args.get("id")
    search_id = request.args.get("search_id") or session.get('search_id')

    # Retrieve the original document from the data source
    original_doc = next((tweet for tweet in DATA if tweet['id'] == int(doc_id)), None)
    document = next((doc for doc in session.get('last_query_documents', {}).values() if str(doc['id']) == doc_id), None)

    if doc_id:
        return render_template("doc_details.html", search_id=search_id, doc_id=doc_id, original=original_doc, document=document)
    else:
        return "Document not found", 404

@app.route('/analytics', methods=['GET'])
def analytics_dashboard():
    analytics = session.get('analytics', {})
    total_requests = len(analytics.get('requests', []))
    total_queries = len(analytics.get('queries', []))
    total_clicks = len(analytics.get('clicks', []))
    total_documents = len(analytics.get('documents', []))

    return render_template('analytics.html', total_requests=total_requests, total_queries=total_queries, total_clicks=total_clicks, total_documents=total_documents)

# -----------------------------------------------
# Run the Application
# -----------------------------------------------

if __name__ == "__main__":
    app.run(port=8088, host="0.0.0.0", threaded=False, debug=True)
