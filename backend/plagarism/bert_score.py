import os
import torch
import json
from sentence_transformers import util
from global_models import get_embedding_model
def compute_bert_similarity(pdf_chunks, compare_chunks):
    if not pdf_chunks or not compare_chunks:
        return None
    model = get_embedding_model()
    pdf_emb = model.embed_documents(pdf_chunks)
    cmp_emb = model.embed_documents(compare_chunks)
    pdf_emb = torch.tensor(pdf_emb)
    cmp_emb = torch.tensor(cmp_emb)
    sim = util.cos_sim(pdf_emb, cmp_emb)
    max_per_pdf = sim.max(dim=1).values
    return float(max_per_pdf.mean())

def bert_scores_from_files(pdf_chunks_file, retrieval_file, output_dir="results"):
    # Load PDF chunks
    with open(pdf_chunks_file, "r", encoding="utf-8") as f:
        pdf_chunks_data = json.load(f)

    # Load retrieval sections
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
        
        score = compute_bert_similarity(pdf_text, retrieved_matches)
        section_scores[section_name] = score

    # Save results
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.basename(pdf_chunks_file).replace(".chunks.json", "")
    output_file = os.path.join(output_dir, f"{base_name}.bert_score.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(section_scores, f, indent=2)

    return section_scores

def bert_scores_from_web(pdf_chunks_file, web_results_file, output_dir="results"):
    # Load PDF chunks
    with open(pdf_chunks_file, "r", encoding="utf-8") as f:
        pdf_chunks_data = json.load(f)

    # Load web results
    with open(web_results_file, "r", encoding="utf-8") as f:
        web_data = json.load(f)

    web_chunks = [item.get("content", "") for item in web_data.get("search_results", [])]

    section_scores = {}
    for pdf_chunk in pdf_chunks_data:
        section_name = pdf_chunk.get("section", "Unknown Section")
        pdf_text = [pdf_chunk.get("text", "")]
        
        score = compute_bert_similarity(pdf_text, web_chunks)
        section_scores[section_name] = score

    # Save results
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.basename(pdf_chunks_file).replace(".chunks.json", "")
    output_file = os.path.join(output_dir, f"{base_name}.web_bert_score.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(section_scores, f, indent=2)

    return section_scores