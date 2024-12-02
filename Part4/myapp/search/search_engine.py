import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
from datetime import datetime, timezone
from myapp.search.objects import ResultItem, Document
from nltk import SnowballStemmer
from nltk.corpus import stopwords
import re
import string
import json

class SearchEngine:
    """Educational search engine implementing multiple ranking algorithms."""

    def __init__(self, corpus, data):
        """
        Initialize the search engine with a corpus.
        """
        self.corpus = corpus
        self.documents = list(corpus.values())
        self.tokenized_tweets = [doc.content.split() for doc in self.documents]
        self.data = data
        self.search_results = {}

    # Helper function from previous part
    def _build_terms(self, line):
        # stemmer = PorterStemmer()
        stemmer = SnowballStemmer("english")
        stop_words = set(stopwords.words("english"))
        line = line.lower()

        # Handle contractions by removing possessive endings and common contractions
        line = re.sub(r"\b(\w+)'s\b", r'\1', line)  # Changes "people's" to "people"
        line = re.sub(r"\b(\w+)n't\b", r'\1 not', line)  # Changes "isn't" to "is not"
        line = re.sub(r"\b(\w+)'ll\b", r'\1 will', line)  # Changes "I'll" to "I will"
        line = re.sub(r"\b(\w+)'d\b", r'\1 would', line)  # Changes "I'd" to "I would"
        line = re.sub(r"\b(\w+)'re\b", r'\1 are', line)  # Changes "you're" to "you are"
        line = re.sub(r"\b(\w+)'ve\b", r'\1 have', line)  # Changes "I've" to "I have"

        line = line.split()

        table = str.maketrans('', '', string.punctuation)
        line = [w.translate(table) for w in line]
        line = [w for w in line if w not in stop_words]
        line = [stemmer.stem(w) for w in line] 
        return ' '.join(line)

    def search(self, search_query, search_id, algorithm="tfidf", top_n=20):
        """
        Perform a search using the specified algorithm and return the results.
        """
        query = self._build_terms(search_query)
        print(f"Search query: {query}")
        print(f"algo {algorithm}")
        if algorithm == "tfidf":
            return self._search_tfidf(query, search_id, top_n)
        elif algorithm == "bm25":
            return self._search_bm25(query, search_id, top_n)
        elif algorithm == "our_score":
            return self._search_custom_score(query, search_id, top_n)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

    def _search_tfidf(self, query, search_id, top_n):
        """
        Search using TF-IDF and return top N results.
        """
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform([doc.content for doc in self.documents])
        query_vector = tfidf_vectorizer.transform([query])
        scores = cosine_similarity(query_vector, tfidf_matrix).flatten()

        top_indices = np.argsort(-scores)[:top_n]
        out = self._build_results(top_indices, scores, search_id)
        return out

    def _search_bm25(self, query, search_id, top_n):
        """
        Search using BM25 and return top N results.
        """
        bm25 = BM25Okapi(self.tokenized_tweets)
        query_tokens = query.split()
        scores = bm25.get_scores(query_tokens)

        top_indices = np.argsort(-scores)[:top_n]
        out = self._build_results(top_indices, scores, search_id)
        return out

    def _search_custom_score(self, query, search_id, top_n):
        """
        Search using a custom scoring algorithm (combining relevance, popularity, and recency).
        """
        text_scores = self._search_tfidf(query, search_id, top_n)
        recency_scores = self._calculate_recency_scores()
        social_scores = self._calculate_social_scores()

        combined_scores = 0.55 * text_scores + 0.3 * social_scores + 0.15 * recency_scores
        top_indices = np.argsort(-combined_scores)[:top_n]

        out = self._build_results(top_indices, combined_scores, search_id)
        return out

    def _calculate_recency_scores(self):
        """
        Compute recency scores for all documents.
        """
        current_date = datetime.now(timezone.utc)
        dates = [datetime.fromisoformat(doc.date) for doc in self.documents]
        recency = [(current_date - date).total_seconds() for date in dates]
        return 1 / (np.array(recency) + 1)

    def _calculate_social_scores(self):
        """
        Compute social popularity scores for all documents.
        """
        likes = np.array([doc.likes for doc in self.documents])
        retweets = np.array([doc.retweets for doc in self.documents])
        return 0.3 * likes + 0.7 * retweets

    def _format_datetime(self, input_time):
        # Parse the input time string to the desired format
        try:
            parsed_time = datetime.fromisoformat(input_time)
            formatted_time = parsed_time.strftime('%Y-%m-%d %H:%M:%S')
            return formatted_time
        except ValueError:
            return input_time
    
    def _format_language(self, lang):
        lang_map = {'en': 'english', 'es': 'spanish', 'fr': 'french', 'de': 'german', 'da': 'danish', 'nl': 'dutch', 'it': 'italian', 'fi': 'finnish', 'ru': 'russian', 'el': 'greek', 'no': 'norwegian', 'pt': 'portuguese', 'sv': 'swedish', 'ar': 'arabic', 'zh': 'chinese', 'hi': 'hindi', 'ja': 'japanese', 'ko': 'korean', 'vi': 'vietnamese', 'th': 'thai', 'bn': 'bengali', 'ta': 'tamil', 'te': 'telugu', 'ur': 'urdu', 'mr': 'marathi', 'pa': 'punjabi', 'gu': 'gujarati', 'pl': 'polish', 'tr': 'turkish', 'he': 'hebrew', 'uk': 'ukrainian', 'ro': 'romanian', 'bg': 'bulgarian', 'cs': 'czech', 'hu': 'hungarian', 'sk': 'slovak', 'lt': 'lithuanian', 'lv': 'latvian', 'et': 'estonian', 'id': 'indonesian', 'ms': 'malay', 'fa': 'persian', 'am': 'amharic', 'sw': 'swahili', 'yo': 'yoruba', 'zu': 'zulu', 'af': 'afrikaans', 'is': 'icelandic', 'ga': 'irish', 'cy': 'welsh', 'eu': 'basque', 'ca': 'catalan', 'sr': 'serbian', 'hr': 'croatian', 'bs': 'bosnian', 'mk': 'macedonian', 'sq': 'albanian', 'hy': 'armenian', 'mn': 'mongolian', 'km': 'khmer', 'lo': 'lao', 'my': 'burmese', 'ne': 'nepali', 'si': 'sinhala', 'jv': 'javanese', 'su': 'sundanese'}
        # lang_code = lang[0] if lang and isinstance(lang, tuple) else None
        return lang_map.get(lang, "Unknown")

    def _build_results(self, top_indices, scores, search_id):
        """
        Construct ResultItem objects for the top-ranked documents.
        """
        results = []

        for idx in top_indices:
            doc = self.documents[idx]
            original_doc = next((original_tweet for original_tweet in self.data if original_tweet['id'] == doc.id), None)

            results.append(ResultItem(
                id=doc.id,
                content=doc.content if original_doc is None else original_doc['content'],
                hashtags=doc.hashtags,
                url=f"doc_details?id={doc.id}&search_id={search_id}",
                tweet_url=doc.url, # Original link
                ranking=scores[idx],
                date=self._format_datetime((doc.date)),
                likes=doc.likes,
                retweets=doc.retweets,
                lang=self._format_language(doc.language),
                user_name=None if original_doc is None else original_doc['user']['displayname'],
                user_id=None if original_doc is None else original_doc['user']['id']
            ))
        
        self.search_results[search_id] = results

        return results
    
    def get_results_by_id(self, search_id):
        # Retrieve results by search_id
        return self.search_results.get(search_id, [])
    
