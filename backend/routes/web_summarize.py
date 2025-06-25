from flask import Blueprint, request, jsonify
from services.summarize_service import summarize_text
import requests
from readability import Document
from bs4 import BeautifulSoup
from services.summarize_service import summarize_text

web_bp = Blueprint('web', __name__, url_prefix='/web')

@web_bp.route('/summarize-url', methods=['POST'])
def summarize_by_url():
    data = request.get_json() or {}
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        #Fetch page HTML
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        resp.raise_for_status()

        #Extract with Readability
        doc = Document(resp.text)
        main_html = doc.summary()
        text = ' '.join(BeautifulSoup(main_html, 'lxml').stripped_strings)

        #Summarize
        summary = summarize_text(text)
        return jsonify({'summary': summary})

    except Exception as e:
        return jsonify({'error': str(e)}), 500