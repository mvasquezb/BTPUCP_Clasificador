import string
import re

from nltk.corpus import stopwords as sw
from nltk import wordpunct_tokenize
from nltk.stem.snowball import SpanishStemmer
from nltk import sent_tokenize
from nltk import pos_tag

from sklearn.base import BaseEstimator, TransformerMixin


class TextProcessor(BaseEstimator, TransformerMixin):

    def __init__(self,
                 stopwords=None,
                 punct=None,
                 lower=True,
                 strip=True):
        self.lower = lower
        self.do_strip = strip
        self.stopwords = stopwords or set(
            sw.words('english') + sw.words('spanish') + ['y/o']
        )
        self.punct = punct or set(string.punctuation + '•')
        self.stemmer = SpanishStemmer()

    def fit(self, X, y=None):
        return self

    def inverse_transform(self, X):
        return [" ".join(doc) for doc in X]

    def transform(self, X):
        return [
            list(self.tokenize(doc)) for doc in X
        ]

    def tokenize(self, document):
        # Break the document into sentences
        for sentence in sent_tokenize(document):
            # Break the sentence into part of speech tagged tokens
            for token, tag in pos_tag(wordpunct_tokenize(sentence)):
                # Apply preprocessing to the token
                token = token.lower() if self.lower else token
                token = self.strip(token) if self.do_strip else token
                token = self.remove_numbers(token)

                # If stopword, ignore token and continue
                if token in self.stopwords:
                    continue

                # If punctuation, ignore token and continue
                if all(char in self.punct for char in token):
                    continue

                # Lemmatize the token and yield
                stemmed = self.stem(token)
                yield stemmed

    def stem(self, token):
        return self.stemmer.stem(token)

    def remove_numbers(self, token):
        return re.sub(r'\d+', '', token)

    def strip(self, token):
        token = re.sub('\s+', '', token)
        token = token.strip()
        token = token.strip('_')
        token = token.strip('*')
        return token
