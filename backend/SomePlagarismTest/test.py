import os
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
import trafilatura
import re
import time
import random
import nltk
import tempfile

# --- Config ---
MAX_PDF_PAGES = 20
MAX_PAGES_TO_PARSE = 20
ENABLE_DEBUG = True
CACHE_FETCHED_URLS = {}

# --- Setup ---
nltk.download("punkt")
model = SentenceTransformer("all-MiniLM-L6-v2")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

def extract_paragraphs_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    paragraphs = [p.strip() for p in full_text.split("\n\n") if len(p.strip()) > 40]
    return paragraphs

def search_scholar(query, max_results=10):
    short_query = " ".join(query.split()[:20])
    query_url = f"https://scholar.google.com/scholar?q={short_query.replace(' ', '+')}"
    if ENABLE_DEBUG:
        print(f"  Querying: {short_query}")
    resp = requests.get(query_url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")

    results = []
    for result in soup.select(".gs_ri")[:max_results]:
        title_tag = result.select_one(".gs_rt a")
        if not title_tag:
            continue
        results.append(title_tag['href'])
    return results

def fetch_content(url):
    if url in CACHE_FETCHED_URLS:
        if ENABLE_DEBUG:
            print(f"     Using cached content for: {url}")
        return CACHE_FETCHED_URLS[url]

    try:
        if ENABLE_DEBUG:
            print(f"     Trying to fetch: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        html = response.text

        pdf_link = None

        if "dl.acm.org" in url:
            soup = BeautifulSoup(html, "html.parser")
            pdf_btn = soup.find("a", href=re.compile(r"/doi/pdf/"))
            if pdf_btn and pdf_btn.get("href"):
                pdf_link = "https://dl.acm.org" + pdf_btn["href"]
        elif url.lower().endswith(".pdf") or "pdf" in url.lower():
            pdf_link = url

        if pdf_link:
            if ENABLE_DEBUG:
                print(f"     Found PDF link: {pdf_link}")
            response = requests.get(pdf_link, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                print("     Failed to download PDF.")
                return None

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp_pdf:
                tmp_pdf.write(response.content)
                tmp_pdf.flush()

                doc = fitz.open(tmp_pdf.name)
                if doc.page_count > MAX_PDF_PAGES:
                    if ENABLE_DEBUG:
                        print(f"     Skipped PDF (Too many pages: {doc.page_count})")
                    return None

                text = ""
                for i in range(min(doc.page_count, MAX_PAGES_TO_PARSE)):
                    text += doc[i].get_text()
                if ENABLE_DEBUG:
                    print(f"     Parsed PDF ({min(doc.page_count, MAX_PAGES_TO_PARSE)} pages)")
        else:
            text = trafilatura.extract(html)
            if ENABLE_DEBUG:
                print("     Extracted webpage content")

        if text and len(text) > 100:
            CACHE_FETCHED_URLS[url] = text
            return text
        else:
            if ENABLE_DEBUG:
                print("     Content too short or empty.")
            return None

    except Exception as e:
        if ENABLE_DEBUG:
            print(f"     Fetch error: {e}")
        return None

def split_into_phrases(text, min_len=4, max_len=10):
    words = nltk.word_tokenize(text)
    phrases = []
    for i in range(len(words)):
        for j in range(i + min_len, min(i + max_len, len(words)) + 1):
            phrase = " ".join(words[i:j])
            if len(phrase.split()) >= min_len:
                phrases.append(phrase)
    return phrases

def find_similar_phrases(chunk, source_text, threshold=0.75):
    your_phrases = split_into_phrases(chunk)
    source_phrases = split_into_phrases(source_text)

    matches = []
    for your_p in your_phrases:
        your_emb = model.encode(your_p, convert_to_tensor=True)
        for src_p in source_phrases:
            src_emb = model.encode(src_p, convert_to_tensor=True)
            sim = float(util.cos_sim(your_emb, src_emb))
            if sim > threshold:
                matches.append((your_p, src_p))
    return matches

def process_pdf(pdf_path):
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    report_path = f"plagiarism_report_{pdf_name}.txt"
    with open(report_path, "w", encoding="utf-8") as report_file:

        print(f"\nProcessing PDF: {pdf_name}")
        report_file.write(f"Report for: {pdf_name}\n\n")

        paragraphs = extract_paragraphs_from_pdf(pdf_path)

        for idx, para in enumerate(paragraphs):
            print(f"\nParagraph {idx+1}: {para[:80]}...")
            report_file.write(f"\nParagraph {idx+1}:\n{para}\n")

            search_results = search_scholar(para)
            if not search_results:
                print("  No search results found.")
                report_file.write("  No search results found.\n")
                continue

            found_match = False
            for url in search_results:
                print(f"  Checking: {url}")
                content = fetch_content(url)
                if not content:
                    print("     Could not fetch content.")
                    continue

                matches = find_similar_phrases(para, content)
                if matches:
                    print("     Partial Matches Found:")
                    report_file.write(f"  Matches found from: {url}\n")
                    for your_line, matched_line in matches:
                        print(f"       Phrase: {your_line}")
                        print(f"         Match: {matched_line}\n")

                        report_file.write(f"    Phrase: {your_line}\n")
                        report_file.write(f"    Match: {matched_line}\n\n")
                    found_match = True
                    break
                else:
                    print("     No similar phrases in this result.")
            if not found_match:
                print("  No matches found for this paragraph.")
                report_file.write("  No matches found.\n")

            time.sleep(random.uniform(2, 4))

def process_all_pdfs(folder_path):
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
    if not pdf_files:
        print("No PDF files found in the directory.")
        return

    for file in pdf_files:
        process_pdf(os.path.join(folder_path, file))

if __name__ == "__main__":
    folder = "pdfs_to_check"
    process_all_pdfs(folder)
