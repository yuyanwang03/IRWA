import pandas as pd
from myapp.search.objects import Document

_corpus = {}

def load_corpus(path) -> dict:
    """
    Loads tweets data from a CSV file into the corpus dictionary.
    """
    # Load the CSV file
    df = pd.read_csv(path)

    # Ensure necessary columns are present 
    required_columns = {'id', 'content', 'date', 'hashtags', 'likes', 'retweets', 'url', 'language', 'docId'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"The CSV must contain the following columns: {required_columns}")

    # Fill the corpus dictionary with Document objects
    df.apply(_row_to_doc_dict, axis=1)

    return _corpus


def _row_to_doc_dict(row: pd.Series):
    """
    Converts a row of the DataFrame to a Document object and adds it to the corpus.
    """
    _corpus[row['docidId']] = Document(
        id=row['id'], 
        content=row['content'], 
        date=row['date'], 
        hashtags=row['hashtags'], 
        likes=row['likes'], 
        retweets=row['retweets'], 
        url=row['url']
    )

