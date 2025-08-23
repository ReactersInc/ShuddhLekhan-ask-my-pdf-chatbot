import os
import json
import argparse

from .web_chunk import load_pdf_chunks, load_web_chunks 
from .arxiv_chunk import load_arxiv_chunks
from .tfidf_score import compute_tfidf_similarity
from .bert_score import compute_bert_similarity

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
    pdf_chunks = load_pdf_chunks(pdf_chunks_path)
    web_chunks = load_web_chunks("scraped_data/web/web_results.json")
    arxiv_chunks, arxiv_pdf_count = load_arxiv_chunks("scraped_data/arxiv/pdfs")
    web_docs_count = _count_unique_web_docs("scraped_data/web/web_results.json")
    combined_sources_count = web_docs_count + (arxiv_pdf_count or 0)
    results = {
        "pdf_file": os.path.basename(pdf_chunks_path),
        "web": {
            "tfidf_similarity": compute_tfidf_similarity(pdf_chunks, web_chunks),
            "bert_similarity": compute_bert_similarity(pdf_chunks, web_chunks),
            "web_chunks_count": len(web_chunks),
            "web_docs_count": web_docs_count,

        },
        "arxiv": {
            "tfidf_similarity": compute_tfidf_similarity(pdf_chunks, arxiv_chunks),
            "bert_similarity": compute_bert_similarity(pdf_chunks, arxiv_chunks),
            "arxiv_chunks_count": len(arxiv_chunks),
            "arxiv_pdf_count": arxiv_pdf_count
        }
    }
        
    combined_chunks = []
    if web_chunks:
        combined_chunks.extend(web_chunks)
    if arxiv_chunks:
        combined_chunks.extend(arxiv_chunks)

    # compute similarity against the combined corpus
    combined_tfidf = None
    combined_bert = None
    if combined_chunks:
        combined_tfidf = compute_tfidf_similarity(pdf_chunks, combined_chunks)
        combined_bert  = compute_bert_similarity(pdf_chunks, combined_chunks)

    
    def _r4(x):
        return None if x is None else round(float(x), 4)

    results["combined"] = {
        "tfidf_similarity": _r4(combined_tfidf),
        "bert_similarity": _r4(combined_bert),
        "combined_chunks_count": len(combined_chunks),
        "web_chunks_count": len(web_chunks),
        "arxiv_chunks_count": len(arxiv_chunks),
        "arxiv_pdf_count": arxiv_pdf_count,
        "sources_count": combined_sources_count
    }
    
    def _norm0(x):
        return 0.0 if x is None else float(x)

    comb_tfidf_val = _norm0(combined_tfidf)
    comb_bert_val  = _norm0(combined_bert)

    # If both are None (no combined chunks), overall_similarity stays None
    overall_similarity = None
    if combined_chunks:
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
    print("Saved", outpath, "->", results)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_chunks_path", help="path to uploaded pdf chunks json (results/<file>.chunks.json)")
    args = parser.parse_args()
    main(args.pdf_chunks_path)
