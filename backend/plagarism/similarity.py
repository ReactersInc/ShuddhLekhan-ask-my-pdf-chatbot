import os
import json
import argparse
from flask import request
from werkzeug.utils import secure_filename

from .web_chunk import load_web_chunks 
from .arxiv_chunk import load_arxiv_chunks
from .tfidf_score import tfidf_scores_from_files
from .bert_score import bert_scores_from_files
from .tfidf_score import tfidf_scores_from_web
from .bert_score import bert_scores_from_web

def _count_unique_web_docs(web_results_path="scraped_data/web/web_results.json"):
    """Return number of unique web documents (unique 'url' entries) found in web_results.json."""
    if not os.path.exists(web_results_path):
        return 0
    try:
        with open(web_results_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return 0
    urls = []
    for item in data.get("search_results", []):
        if isinstance(item, dict):
            url = item.get("url")
            if url:
                urls.append(url)
    return len(set(urls))


def main(pdf_chunks_path):
    results = {}
    file = request.files["file"]
    filename = secure_filename(file.filename)
    base_filename, _ = os.path.splitext(filename)
    pdf_chunks_file = f"results/{base_filename}.chunks.json"
    retrieval_file = f"results/retrieval/{base_filename}_topk.json"

    tfidf_section_scores = tfidf_scores_from_files(pdf_chunks_file, retrieval_file)
    bert_section_scores = bert_scores_from_files(pdf_chunks_file, retrieval_file)

    web_tfidf_scores = tfidf_scores_from_web(pdf_chunks_file=pdf_chunks_path,web_results_file="scraped_data/web/web_results.json")
    web_bert_scores = bert_scores_from_web(pdf_chunks_file=pdf_chunks_path,web_results_file="scraped_data/web/web_results.json")

    def _average_section_scores(path):
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return None
        scores = list(data.values()) if isinstance(data, dict) else []
        if not scores:
            return None
        return round(sum(scores) / len(scores), 4)
    arxiv_tfidf_path = f"results/{base_filename}.tfidf.json"
    arxiv_bert_path  = f"results/{base_filename}.bert_score.json"

    web_tfidf_path = f"results/{base_filename}.web_tfidf.json"
    web_bert_path  = f"results/{base_filename}.web_bert_score.json"

    web_chunks = load_web_chunks("scraped_data/web/web_results.json")
    arxiv_chunks, arxiv_pdf_count = load_arxiv_chunks("scraped_data/arxiv/pdfs")
    web_docs_count = _count_unique_web_docs("scraped_data/web/web_results.json")
    combined_sources_count = web_docs_count + (arxiv_pdf_count or 0)

    # --- Compute weighted global scores for all sources ---
    def _weighted_global_score(web_score, web_count, arxiv_score, arxiv_count):
        if web_score is None and arxiv_score is None:
            return None
        web_val = web_score or 0.0
        arxiv_val = arxiv_score or 0.0
        total_count = (web_count or 0) + (arxiv_count or 0)
        if total_count == 0:
            return None
        weighted = (web_val * (web_count or 0) + arxiv_val * (arxiv_count or 0)) / total_count
        return round(weighted, 4)


    results = {
        "pdf_file": os.path.basename(pdf_chunks_path),
        "retrieval": {
            "tfidf_section_scores": tfidf_section_scores,
            "bert_section_scores": bert_section_scores
        },
        "web": {
            "tfidf_section_scores": web_tfidf_scores, 
            "bert_section_scores": web_bert_scores,
            "tfidf_global": _average_section_scores(web_tfidf_path),
            "bert_global": _average_section_scores(web_bert_path),
            "web_chunks_count": len(web_chunks),
            "web_docs_count": web_docs_count,

        },
        "arxiv": {
            "arxiv_chunks_count": len(arxiv_chunks),
            "arxiv_pdf_count": arxiv_pdf_count,
            "tfidf_global": _average_section_scores(arxiv_tfidf_path),
            "bert_global": _average_section_scores(arxiv_bert_path)
        }
    }
    results["global"] = {
    "tfidf_global": _weighted_global_score(
        results["web"]["tfidf_global"], len(web_chunks),
        results["arxiv"]["tfidf_global"], len(arxiv_chunks)
    ),
    "bert_global": _weighted_global_score(
        results["web"]["bert_global"], len(web_chunks),
        results["arxiv"]["bert_global"], len(arxiv_chunks)
    )
    }


    results["combined"] = {
        "web_chunks_count": len(web_chunks),
        "arxiv_chunks_count": len(arxiv_chunks),
        "arxiv_pdf_count": arxiv_pdf_count,
        "sources_count": combined_sources_count
    }
    
    def _norm0(x):
        return 0.0 if x is None else float(x)

    # Use global weighted scores for overall similarity
    comb_tfidf_val = _norm0(results["global"]["tfidf_global"])
    comb_bert_val  = _norm0(results["global"]["bert_global"])

    # If both are None, overall_similarity stays None
    overall_similarity = None
    if comb_tfidf_val is not None or comb_bert_val is not None:
        overall_val = 0.6 * comb_bert_val + 0.4 * comb_tfidf_val
        overall_similarity = round(float(overall_val), 4)

    # attach to results
    results["combined"]["overall_similarity"] = overall_similarity
    # also provide a percent string for easy UI display (None-safe)
    results["combined"]["overall_percent"] = None if overall_similarity is None else f"{(overall_similarity * 100):.2f}%"

    os.makedirs("results", exist_ok=True)
    outpath = os.path.join("results", "similarity_report.json")
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_chunks_path", help="path to uploaded pdf chunks json (results/<file>.chunks.json)")
    args = parser.parse_args()
    main(args.pdf_chunks_path)
