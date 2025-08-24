from global_models import get_embedding_model
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
import os, json


def embed_sections(json_file, embedding_model=None):
    if embedding_model is None:
        embedding_model = get_embedding_model()

    if not os.path.exists(json_file):
        raise FileNotFoundError(f"Chunks JSON not found: {json_file}")

    with open(json_file, "r", encoding="utf-8") as f:
        sections = json.load(f)

    docs = []
    base_name = os.path.basename(json_file).replace(".chunks.json", "")

    for sec in sections:
        section_name = sec.get("section", "Unknown")
        text = sec.get("text", "").strip()
        if not text:
            continue

        docs.append(Document(
            page_content=text,
            metadata={
                "source": base_name,
                "section": section_name
            }
        ))

    persist_dir = os.path.join("results", f"{base_name}_sections_store")
    os.makedirs(persist_dir, exist_ok=True)

    faiss_db = FAISS.from_documents(docs, embedding_model)
    faiss_db.save_local(persist_dir)

    print(f"✅ Embedded {len(docs)} sections into {persist_dir}")
    return persist_dir
