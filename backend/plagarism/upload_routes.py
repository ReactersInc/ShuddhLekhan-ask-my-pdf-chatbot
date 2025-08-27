#upload_routes.py
# """
# Purpose:
# --------
# Defines the Flask API route for handling plagiarism PDF uploads. # This route orchestrates the entire plagiarism-checking pipeline:
# 1. Receives and stores the uploaded PDF.
# 2. Processes the PDF into section-based chunks.
# 3. Extracts keywords, key phrases, and key points using LLM.
# 4. (Future) Initiates web scraping for related content.
# 5. (Future) Runs a Cython-based plagiarism checker.
# Responsibilities:
# -----------------
# - Validate and securely store uploaded files.
# - Call service layer modules for PDF processing and keyword extraction.
# - Prepare JSON responses for the client.
# - Manage any future pipeline steps (scraping, plagiarism detection).
# Note:
# -----
# This route does NOT contain PDF parsing, keyword extraction, or scraping logic directly.
# All heavy processing is delegated to dedicated services in plagarism/services/.
# """

# from flask import Blueprint, request, jsonify
# from werkzeug.utils import secure_filename
# import os, json
# from pathlib import Path
# from plagarism.pdf_processor import process_pdf
# from plagarism.keyword_extractor import extract_keywords_from_sections

# UPLOAD_DIR = "./plagarism/uploads"
# RESULT_DIR = "./plagarism/results"
# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(RESULT_DIR, exist_ok=True)

# plag_upload_bp = Blueprint("plagiarism_upload_bp", __name__)

# @plag_upload_bp.route("/upload", methods=["POST"])
# def upload_file():
#     if "file" not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400
#     file = request.files["file"]
#     if file.filename == "":
#         return jsonify({"error": "No selected file"}), 400
#     filename = secure_filename(file.filename)
#     file_path = os.path.join(UPLOAD_DIR, filename)
#     file.save(file_path)
#     try:
#         # Step 1: Process PDF into chunks
#         sections, chunks_path = process_pdf(file_path, RESULT_DIR)
#         # Step 2: Extract keywords & key points
#         keyword_results = extract_keywords_from_sections(sections)
#         keywords_path = os.path.join(RESULT_DIR, Path(filename).stem + ".keywords.json")
#         with open(keywords_path, "w", encoding="utf-8") as f:
#             json.dump(keyword_results, f, indent=2, ensure_ascii=False)
#         # Step 3: Future - Scraping & plagiarism checking
#         # scraped_data = scrape_sources(keyword_results)
#         # check_results = run_plagiarism_check(file_path, scraped_data)
#         return jsonify({
#             "message": "File processed successfully",
#             "pdf_path": file_path,
#             "chunks_json": chunks_path,
#             "keywords_json": keywords_path,
#             "sections_count": len(sections)
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

"""
Purpose:
--------
Defines the Flask API route for handling plagiarism PDF uploads. This route orchestrates the entire plagiarism-checking pipeline:
1. Receives and stores the uploaded PDF.
2. Processes the PDF into section-based chunks.
3. Extracts keywords, key phrases, and key points using LLM.
4. Initiates ArXiv data collection for related research papers.
5. Initiates web scraping for related content using Tavily.
6. (Future) Runs plagiarism checker.

Responsibilities:
-----------------
- Validate and securely store uploaded files.
- Call service layer modules for PDF processing and keyword extraction.
- Orchestrate ArXiv and web data collection.
- Prepare JSON responses for the client.
- Manage any future pipeline steps (plagiarism detection).

Note:
-----
This route does NOT contain PDF parsing, keyword extraction, or scraping logic directly. All heavy processing is delegated to dedicated services.
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
import traceback
from pathlib import Path

from .section_chunker import process_pdf_to_sections as process_pdf
from .keyword_extractor import extract_keywords_from_sections
from .arxiv_service import ArxivService
from .tavily_service import TavilyWebService
from .similarity import main as run_similarity
from celery_tasks.embed_pdf_task import embed_pdf_task
from .section_embedded import embed_sections
from .retriever import store_topk_for_sections
from global_models import get_embedding_model
from .sentence_chunker import create_sentence_chunks

UPLOAD_DIR = "./uploads"
RESULT_DIR = "./results"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

plag_upload_bp = Blueprint("plagiarism_upload_bp", __name__)


@plag_upload_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, filename)
    file.save(file_path)

    try:
        print(f"Starting processing for: {filename}")

        # Step 1: Process PDF into chunks (Leader's original functionality)
        print("Processing PDF into chunks...")
        sections, chunks_path = process_pdf(file_path, RESULT_DIR)
        print(f"PDF chunking completed. Found {len(sections)} sections.")
        print("Creating sentence-level subchunks...")
        subchunks_data = create_sentence_chunks(chunks_path, RESULT_DIR)
        subchunks_path = os.path.join(RESULT_DIR, Path(filename).stem + ".subchunks.json")
        print(f"Sentence-level subchunks created: {len(subchunks_data)} chunks")

        # Step 2: Extract keywords & key points (Leader's original functionality)
        print("Starting keyword extraction with LLM...")
        keyword_results = extract_keywords_from_sections(sections)
        print("Keyword extraction completed.")

        keywords_path = os.path.join(RESULT_DIR, Path(filename).stem + ".keywords.json")
        with open(keywords_path, "w", encoding="utf-8") as f:
            json.dump(keyword_results, f, indent=2, ensure_ascii=False)
        print(f"Keywords saved to: {keywords_path}")

        # Step 3: ArXiv Data Collection (Your addition)
        print("Starting ArXiv search and download...")
        arxiv_service = ArxivService()
        arxiv_results = arxiv_service.search_and_download_from_keywords(keywords_path, max_papers=5)
        print("ArXiv collection completed.")
        # Step 3.5: Embed ArXiv PDFs into plagiarism vector store
        print("Starting embedding of ArXiv PDFs into plagiarism vector store...")
    
        arxiv_pdf_dir = os.path.join("scraped_data", "arxiv", "pdfs")
        if os.path.exists(arxiv_pdf_dir):
                for pdf_file in os.listdir(arxiv_pdf_dir):
                    if pdf_file.lower().endswith(".pdf"):
                        pdf_path = os.path.join(arxiv_pdf_dir, pdf_file)
                        arxiv_base_name = os.path.splitext(pdf_file)[0]
                        # queue Celery task → embeddings go into both summarization & plagiarism folders
                        relative_path = os.path.join("arxiv", "pdfs", arxiv_base_name)
                        result = embed_pdf_task.delay(pdf_file, pdf_path, arxiv_base_name, relative_path)
                    print(f"Queued embedding for ArXiv PDF: {pdf_file}")

        # Step 3.6: Embed Section Chunks into plagiarism vector store
        print("Starting embedding of section chunks into plagiarism vector store...")

        results_dir = "results"
        user_base_name = Path(filename).stem 
        if os.path.exists(results_dir):
                for file in os.listdir(results_dir):
                    if file.endswith(".chunks.json"):
                        json_path = os.path.join(results_dir, file)
                        result = embed_sections(json_path)
                        print(f"Queued embedding for section file: {file}")

        chunks_json = os.path.join("results", f"{user_base_name}.chunks.json")
        print("Looking for section chunks at:", chunks_json)
        print("Exists?", os.path.exists(chunks_json))
        embedding_model = get_embedding_model() 
        topk_report_path = store_topk_for_sections(
                section_chunks_json=chunks_json,
                arxiv_vectors_root="vector_store",
                out_dir=os.path.join("results", "retrieval"),
                k=5,
                per_store=2,
                embedding_model=embedding_model
        )
        print(f"Top-K report stored at: {topk_report_path}")

        # Step 4: Web Data Collection using Tavily (Your addition)
        print("Starting web data collection with Tavily...")

        # Create scraped_data structure
        scraped_base_dir = "scraped_data"
        os.makedirs(scraped_base_dir, exist_ok=True)

        # Create web directory
        web_content_dir = os.path.join(scraped_base_dir, "web")
        os.makedirs(web_content_dir, exist_ok=True)

        # Extract text chunks from sections for web search
        chunk_texts = []
        for section in sections:
            text = section.get('text', '').strip()
            if len(text) > 100:  # Only use substantial chunks
                chunk_texts.append(text)

        # Limit chunks to avoid overwhelming the API
        if len(chunk_texts) > 8:
            chunk_texts = sorted(chunk_texts, key=len, reverse=True)[:8]

        # Initialize Tavily service and process chunks
        tavily_service = TavilyWebService()
        if tavily_service.is_available() and chunk_texts:
            web_results = tavily_service.search_and_extract_for_chunks(
                chunks=chunk_texts,
                web_content_dir=web_content_dir,
                max_results_per_chunk=2,
            )
            print(f"Web collection completed: {web_results.get('content_extracted', 0)} contents extracted")
        else:
            print("Tavily service not available or no chunks to process")
            web_results = {
                'success': False,
                'error': 'Tavily service not available or no chunks',
                'content_extracted': 0,
                'chunks_processed': 0,
                'urls_found': 0,
                'quality_distribution': {},
                'total_word_count': 0,
                'storage_path': '',
                'summary_file': ''
            }

        # Step 5: Future - plagiarism checking (Leader's original comment)
        # scraped_data = scrape_sources(keyword_results)
        # check_results = run_plagiarism_check(file_path, scraped_data)

        print("Running similarity pipeline...")
        similarity_results = run_similarity(chunks_path)
        print("Similarity pipeline completed.")

        overall_percent = None
        sources = None
        combined_section = similarity_results.get("combined", {}) if isinstance(similarity_results, dict) else {}
        overall = combined_section.get("overall_similarity")
        overall_percent = None if overall is None else round(float(overall) * 100, 2)
        sources = combined_section.get("sources_count")


        # Return response combining leader's original format + your additions
        return jsonify({
            "message": "File processed successfully with ArXiv and Web data collection",
            "pdf_path": file_path,
            "chunks_json": chunks_path,
            "keywords_json": keywords_path,
            "sections_count": len(sections),
            "keyword_results_count": len(keyword_results),
            "subchunks_json": subchunks_path,
            "arxiv_collection": {
                "success": arxiv_results.get('success', False),
                "papers_found": arxiv_results.get('papers_found', 0),
                "papers_downloaded": arxiv_results.get('papers_downloaded', 0),
                "storage_paths": arxiv_results.get('storage_paths', {}),
                "query_used": arxiv_results.get('query', ''),
                "keywords_used": arxiv_results.get('keywords_used', [])[:5]
            },
            "web_collection": {
                "success": web_results.get('success', False),
                "chunks_processed": web_results.get('chunks_processed', 0),
                "urls_found": web_results.get('urls_found', 0),
                "content_extracted": web_results.get('content_extracted', 0),
                "quality_distribution": web_results.get('quality_distribution', {}),
                "total_word_count": web_results.get('total_word_count', 0),
                "storage_path": web_results.get('storage_path', ''),
                "summary_file": web_results.get('summary_file', '')
            },
            "overallSimilarity": overall_percent,
            "sources": sources,
            "similarity_results": similarity_results
        })

    except Exception as e:
        error_msg = f"Error processing {filename}: {str(e)}"
        print(f"Error: {error_msg}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        return jsonify({
            "error": error_msg,
            "file": filename,
            "type": "processing_error"
        }), 500
