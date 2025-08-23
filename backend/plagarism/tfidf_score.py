import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_tfidf_similarity(pdf_chunks, compare_chunks):
    if not pdf_chunks:
        raise ValueError("No pdf chunks to compare.")
    if not compare_chunks:
        return None
    all_texts = pdf_chunks + compare_chunks
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    pdf_vecs = tfidf_matrix[:len(pdf_chunks)]
    cmp_vecs = tfidf_matrix[len(pdf_chunks):]
    if cmp_vecs.shape[0] == 0:
        return None
    sim = cosine_similarity(pdf_vecs, cmp_vecs)
    max_per_pdf = np.max(sim, axis=1)
    return float(np.mean(max_per_pdf))
