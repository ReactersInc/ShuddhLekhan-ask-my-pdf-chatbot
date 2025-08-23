def compute_bert_similarity(pdf_chunks, compare_chunks):
    try:
        from sentence_transformers import SentenceTransformer, util
    except Exception:
        return None
    if not pdf_chunks or not compare_chunks:
        return None
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    pdf_emb = model.encode(pdf_chunks, convert_to_tensor=True)
    cmp_emb = model.encode(compare_chunks, convert_to_tensor=True)
    sim = util.cos_sim(pdf_emb, cmp_emb)
    max_per_pdf = sim.max(dim=1).values
    return float(max_per_pdf.mean())
