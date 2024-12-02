import json

class Document:
    """
    Represents a tweet from the corpus.
    """
    def __init__(self, id, content, date, hashtags, likes, retweets, url, language):
        self.id = id
        self.content = content
        self.date = date
        self.hashtags = hashtags
        self.likes = likes
        self.retweets = retweets
        self.url = url
        self.language = language

    def to_json(self):
        """
        Convert the Document object to a JSON-like dictionary.
        """
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string.
        """
        return json.dumps(self.__dict__)

class ResultItem:
    """
    Represents a search result.
    """
    def __init__(self, id, content, hashtags, url, tweet_url, ranking, date, likes, retweets, lang=None, user_name=None, user_id=None):
        self.id = id
        self.content = content
        self.hashtags = hashtags
        self.url = url
        self.tweet_url = tweet_url
        self.ranking = ranking
        self.date = date
        self.likes = likes
        self.retweets = retweets
        self.language = lang,
        self.user_name = user_name
        self.user_id = user_id
