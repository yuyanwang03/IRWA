import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
from datetime import datetime, timezone
from myapp.search.objects import ResultItem, Document

class SearchEngine:
    """Educational search engine implementing multiple ranking algorithms."""

    def __init__(self, corpus):
        """
        Initialize the search engine with a corpus.
        """
        self.corpus = corpus
        self.documents = list(corpus.values())
        self.tokenized_tweets = [doc.content.split() for doc in self.documents]

    def search(self, search_query, search_id, algorithm="tfidf", top_n=20):
        """
        Perform a search using the specified algorithm and return the results.
        """
        print(f"Search query: {search_query}")
        if algorithm == "tfidf":
            return self._search_tfidf(search_query, search_id, top_n)
        elif algorithm == "bm25":
            return self._search_bm25(search_query, search_id, top_n)
        elif algorithm == "our_score":
            return self._search_custom_score(search_query, search_id, top_n)
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
        return self._build_results(top_indices, scores, search_id)

    def _search_bm25(self, query, search_id, top_n):
        """
        Search using BM25 and return top N results.
        """
        bm25 = BM25Okapi(self.tokenized_tweets)
        query_tokens = query.split()
        scores = bm25.get_scores(query_tokens)

        top_indices = np.argsort(-scores)[:top_n]
        return self._build_results(top_indices, scores, search_id)

    def _search_custom_score(self, query, search_id, top_n):
        """
        Search using a custom scoring algorithm (combining relevance, popularity, and recency).
        """
        text_scores = self._search_tfidf(query, search_id, top_n)
        recency_scores = self._calculate_recency_scores()
        social_scores = self._calculate_social_scores()

        combined_scores = 0.55 * text_scores + 0.3 * social_scores + 0.15 * recency_scores
        top_indices = np.argsort(-combined_scores)[:top_n]

        return self._build_results(top_indices, combined_scores, search_id)

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

    def _build_results(self, top_indices, scores, search_id):
        """
        Construct ResultItem objects for the top-ranked documents.
        """
        results = []
        for idx in top_indices:
            doc = self.documents[idx]
            results.append(ResultItem(
                id=doc.id,
                content=doc.content,
                author=doc.author,
                url=f"doc_details?id={doc.id}&search_id={search_id}",
                ranking=scores[idx],
                date=doc.date,
                likes=doc.likes,
                retweets=doc.retweets
            ))
        return results
