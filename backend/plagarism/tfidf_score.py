import json
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_tfidf_similarity(pdf_chunks, compare_chunks):
    """
    Compute average max TF-IDF similarity between PDF chunks and comparison chunks.
    pdf_chunks: List of strings (uploaded PDF chunks)
    compare_chunks: List of strings (retrieved top matches for a section)
    Returns: float (average max similarity) or None if compare_chunks is empty
    """
    if not pdf_chunks:
        raise ValueError("No PDF chunks provided.")
    if not compare_chunks:
        return None

    all_texts = pdf_chunks + compare_chunks
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    pdf_vecs = tfidf_matrix[:len(pdf_chunks)]
    cmp_vecs = tfidf_matrix[len(pdf_chunks):]

    if cmp_vecs.shape[0] == 0:
        return None

    sim_matrix = cosine_similarity(pdf_vecs, cmp_vecs)
    max_per_pdf = np.max(sim_matrix, axis=1)
    return float(np.mean(max_per_pdf))


def tfidf_scores_from_files(pdf_chunks_file, retrieval_file,output_dir="results"):
    with open(pdf_chunks_file, "r", encoding="utf-8") as f:
        pdf_chunks_data = json.load(f)
    
    with open(retrieval_file, "r", encoding="utf-8") as f:
        retrieval_data = json.load(f)
    
    section_scores = {}
    for pdf_chunk in pdf_chunks_data:
        section_name = pdf_chunk.get("section", "Unknown Section")
        pdf_text = [pdf_chunk.get("text", "")]
        
        # ✅ Use retrieval_data["sections"]
        retrieved_matches = []
        for retrieval_section in retrieval_data.get("sections", []):
            if retrieval_section.get("section") == section_name:
                for match in retrieval_section.get("top_matches", []):
                    retrieved_matches.append(match.get("text", ""))
        
        score = compute_tfidf_similarity(pdf_text, retrieved_matches)
        section_scores[section_name] = score
    filename = os.path.basename(pdf_chunks_file).replace(".chunks.json", ".tfidf.json")
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(section_scores, f, indent=2, ensure_ascii=False)
    return section_scores

def tfidf_scores_from_web(pdf_chunks_file, web_results_file, output_dir="results"):
    with open(pdf_chunks_file, "r", encoding="utf-8") as f:
        pdf_chunks_data = json.load(f)

    with open(web_results_file, "r", encoding="utf-8") as f:
        web_data = json.load(f)
    web_chunks = [item.get("content", "") for item in web_data.get("search_results", [])]

    section_scores = {}
    for pdf_chunk in pdf_chunks_data:
        section_name = pdf_chunk.get("section", "Unknown Section")
        pdf_text = [pdf_chunk.get("text", "")]
        score = compute_tfidf_similarity(pdf_text, web_chunks)
        section_scores[section_name] = score

    filename = os.path.basename(pdf_chunks_file).replace(".chunks.json", ".web_tfidf.json")
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(section_scores, f, indent=2, ensure_ascii=False)

    return section_scores
