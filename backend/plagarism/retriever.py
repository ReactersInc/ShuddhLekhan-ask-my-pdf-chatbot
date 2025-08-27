# plagiarism/retriever.py
import os, json, glob
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import FAISS
from global_models import get_embedding_model

def _find_faiss_dirs(root: str) -> List[str]:
    """
    Find FAISS persist dirs by looking for index.faiss (LangChain FAISS saves this).
    Returns folder paths that contain the index file.
    """
    dirs = set()
    for path in glob.glob(os.path.join(root, "**", "index.faiss"), recursive=True):
        dirs.add(os.path.dirname(path))
    return sorted(dirs)

def _load_sections_from_json(chunks_json_path: str) -> List[Dict[str, str]]:
    with open(chunks_json_path, "r", encoding="utf-8") as f:
        sections = json.load(f)
    # keep only non-empty text sections
    clean = []
    for s in sections:
        text = (s.get("text") or "").strip()
        if not text:
            continue
        clean.append({"section": s.get("section", "Unknown"), "text": text})
    return clean

def store_topk_for_sections(
    section_chunks_json: str,
    arxiv_vectors_root: str,
    out_dir: str = "results/retrieval",
    k: int = 5,
    per_store: int = 2,
    embedding_model=None
) -> str:
    """
    For each section in results/<file>.chunks.json:
      - query every FAISS store under `arxiv_vectors_root`
      - collect per-store top `per_store` matches
      - take global top `k` matches
      - save report JSON to `out_dir/<base>_topk.json`

    Notes on scores:
      - LangChain FAISS often returns L2 distances (lower = better). We store both raw `distance`
        and a convenience `similarity = 1 / (1 + distance)` for easy 0..1 interpretation.
    """
    if embedding_model is None:
        embedding_model = get_embedding_model()

    os.makedirs(out_dir, exist_ok=True)

    # load sections
    sections = _load_sections_from_json(section_chunks_json)
    base_name = os.path.basename(section_chunks_json).replace(".chunks.json", "")
    arxiv_vectors_root = "vector_store"
    # discover arxiv vector stores
    faiss_dirs = _find_faiss_dirs(arxiv_vectors_root)
    if not faiss_dirs:
        raise FileNotFoundError(f"No FAISS stores found under: {arxiv_vectors_root}")

    report = {
        "filename": base_name,
        "k": k,
        "per_store": per_store,
        "arxiv_vectors_root": arxiv_vectors_root,
        "sections": []
    }

    for sec in sections:
        sec_text = sec["text"]
        sec_name = sec["section"]

        # collect candidates across all stores (lazy-load per store)
        candidates = []
        for store_dir in faiss_dirs:
            try:
                vs = FAISS.load_local(
                    store_dir,
                    embedding_model,
                    allow_dangerous_deserialization=True
                )
                hits = vs.similarity_search_with_score(sec_text, k=per_store)
                for doc, dist in hits:
                    # Normalize to a convenient 0..1 similarity (higher = better)
                    similarity = 1.0 / (1.0 + float(dist)) if dist is not None else None
                    candidates.append({
                        "vector_dir": store_dir,
                        "source": doc.metadata.get("source"),
                        "section": doc.metadata.get("section"),
                        "distance": float(dist),
                        "similarity": similarity,
                        "text": doc.page_content  # preview, cap to keep JSON smaller
                    })
            except Exception as e:
                # skip problematic stores but continue the loop
                print(f"[warn] failed querying {store_dir}: {e}")

        # sort by distance asc (best first) and take global top-k
        candidates.sort(key=lambda c: c["distance"])
        topk = candidates[:k]

        # compute simple average similarity for this section (for later use)
        avg_sim = None
        sims = [c["similarity"] for c in topk if c["similarity"] is not None]
        if sims:
            avg_sim = sum(sims) / len(sims)

        report["sections"].append({
            "section": sec_name,
            "top_matches": topk,
            "avg_similarity": avg_sim
        })

    out_path = os.path.join(out_dir, f"{base_name}_topk.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"✅ Stored top-k retrieval results at: {out_path}")
    return out_path
