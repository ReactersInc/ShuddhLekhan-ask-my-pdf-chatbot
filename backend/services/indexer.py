import os
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from PIL import Image
from global_models import  get_image_captioner
from sentence_transformers import SentenceTransformer
_clip_model = SentenceTransformer("clip-ViT-B-32")

PERSIST_ROOT = "vector_store"

def _caption_image(img: Image.Image) -> str:
    processor, model = get_image_captioner()
    device = next(model.parameters()).device
    inputs = processor(images=img, return_tensors="pt").to(device)
    out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)

def index_pdf_text(
    pdf_name: str, 
    full_text: str, 
    embedding_model,
    tables: list[tuple[str, str]] = None,
    images: list[str] = None,
    table_embedding_model=None,
    image_embedding_model=None,
) -> bool:

    persist_dir = os.path.join(PERSIST_ROOT, pdf_name)
    os.makedirs(persist_dir, exist_ok=True)

    # text
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(full_text)
    text_docs = [Document(page_content=chunk, metadata={"source": pdf_name, "type": "text"}) for chunk in chunks]

    vectordb = Chroma.from_documents(
        documents=text_docs,
        embedding=embedding_model,
        persist_directory=persist_dir,
    )
    print(f"[✔] Added {len(text_docs)} text chunks to vector DB.")
    if text_docs:
        print(f"[DEBUG] First chunk: {text_docs[0].page_content[:300]}")

    # 2) TABLES
    if tables and table_embedding_model:
        table_texts = [table_text for _, table_text in tables]
        table_docs = [
            Document(
                page_content=table_text,
                metadata={
                    "source": f"{pdf_name}::table::{os.path.basename(fn)}",
                    "type": "table"
                }
            )
            for fn, table_text in tables
        ]
        table_vectors = table_embedding_model.embed_documents(table_texts)
        vectordb.add_documents(table_docs, embeddings=table_vectors)
        print(f"[✔] Added {len(table_docs)} table chunks to vector DB.")

    if images and image_embedding_model:
        image_docs = []
        image_inputs = []
        for img_path in images:
            try:
                img = Image.open(img_path).convert("RGB")
                caption = _caption_image(img)
                image_inputs.append(img)
                image_docs.append(
                    Document(
                        page_content="",
                        metadata={
                            "source": f"{pdf_name}::image::{os.path.basename(img_path)}",
                            "type": "image"
                        }
                    )
                )
            except Exception as e:
                print(f"[❌] Skipping image {img_path}: {e}")

        if image_docs:
            image_vectors = _clip_model.encode(
                image_inputs,
                convert_to_tensor=False,
            )
            assert len(image_vectors) == len(image_docs), "Mismatch between images and embeddings!"
            vectordb.add_documents(image_docs, embeddings=image_vectors)
            print(f"[✔] Added {len(image_docs)} image docs to vector DB.")

    vectordb.persist()
    print("[✔] Vector DB persisted to disk.")
    return True
