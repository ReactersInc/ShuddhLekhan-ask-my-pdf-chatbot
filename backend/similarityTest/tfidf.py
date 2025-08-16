from typing import Iterable
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def fit_vectorizer(corpus: Iterable[str], ngram_range=(1, 3), max_features=4000) -> TfidfVectorizer:
    vec = TfidfVectorizer(ngram_range=ngram_range, max_features=max_features)
    vec.fit(corpus)
    return vec

def tfidf_similarity_pair(doc_a: str, doc_b: str, ngram_range=(1, 3), max_features=4000) -> float:
    vec = TfidfVectorizer(ngram_range=ngram_range, max_features=max_features)
    m = vec.fit_transform([doc_a, doc_b])
    sim = float(cosine_similarity(m)[0, 1])
    return sim

def tfidf_similarity_matrix(corpus: Iterable[str], ngram_range=(1, 3), max_features=4000) -> np.ndarray:
    vec = TfidfVectorizer(ngram_range=ngram_range, max_features=max_features)
    m = vec.fit_transform(corpus)
    return cosine_similarity(m)
