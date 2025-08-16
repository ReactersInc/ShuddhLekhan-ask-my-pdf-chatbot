"""
Purpose:
--------
Web content scraping service using Tavily API for plagiarism detection.
Searches web content based on PDF text chunks and extracts relevant content.

Responsibilities:
-----------------
- Search web using Tavily API with text chunks as queries
- Extract clean content from URLs using Trafilatura
- Categorize content quality (high/medium/low)
- Store content and metadata in organized structure
- Support batch processing for multiple chunks

Storage Structure:
-----------------
scraped_data/web/
├── content/           # Extracted web content as JSON files
├── metadata/          # Metadata for each extracted content
└── web_results.json   # Summary of all web search results

Note:
-----
Integrates with the plagiarism checker workflow after keyword extraction.
"""

import os
import json
import hashlib
import requests
import logging
import re
from datetime import datetime
from urllib.parse import urlparse
from typing import List, Dict, Any, Optional

# Import trafilatura for content extraction
try:
    import trafilatura
    import trafilatura.settings
except ImportError:
    print("Warning: trafilatura not installed. Install with: pip install trafilatura")
    trafilatura = None

logger = logging.getLogger(__name__)

class TavilyWebService:
    def __init__(self, api_key: str = None):
        # Get API key from environment or parameter
        self.api_key = api_key or os.getenv('TAVILY_API_KEY')
        self.base_url = "https://api.tavily.com/search"
        self.session = requests.Session()
        
        # Configure session with anti-403 headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'no-cache'
        })
        
        if not self.api_key:
            logger.warning("TAVILY_API_KEY not found - web scraping disabled")
    
    def is_available(self) -> bool:
        """Check if Tavily service is available"""
        return bool(self.api_key and trafilatura)
    
    def _create_search_query(self, text: str) -> str:
        """Create an effective search query from chunk text (max 400 chars)"""
        # Clean the text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # If text is short enough, use it directly
        if len(text) <= 400:
            return text
        
        # Extract key phrases and important terms
        important_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Proper nouns
            r'\b(?:algorithm|method|approach|technique|model|framework|system)\b[^.]*',
            r'\b(?:artificial intelligence|machine learning|deep learning|neural network|transformer|BERT|GPT)\b[^.]*',
            r'\b(?:research|study|analysis|implementation|development|optimization)\b[^.]*'
        ]
        
        key_phrases = []
        for pattern in important_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            key_phrases.extend(matches[:2])  # Limit matches per pattern
        
        # If we found key phrases, use them
        if key_phrases:
            query = ' '.join(key_phrases)
            if len(query) <= 400:
                return query
        
        # Fallback: use first 400 characters
        return text[:400].rsplit(' ', 1)[0]  # Break at word boundary
    
    def search_web(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web using Tavily API"""
        if not self.is_available():
            logger.warning("Tavily service not available")
            return []
        
        try:
            # Create effective search query
            search_query = self._create_search_query(query)
            
            logger.info(f"Searching web: {search_query[:100]}...")
            
            headers = {'Content-Type': 'application/json'}
            
            payload = {
                'api_key': self.api_key,
                'query': search_query,
                'search_depth': 'basic',
                'include_answer': False,
                'include_images': False,
                'include_raw_content': False,
                'max_results': max_results
            }
            
            response = self.session.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            logger.info(f"Found {len(results)} web results")
            return results
            
        except requests.RequestException as e:
            logger.error(f"Tavily search error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in web search: {str(e)}")
            return []
    
    def _determine_content_quality(self, text: str, url: str) -> tuple:
        """Determine content quality (high/medium/low) and quality score"""
        quality_score = 0.5  # Default
        
        # Length scoring
        if len(text) > 2000:
            quality_score += 0.2
        elif len(text) > 1000:
            quality_score += 0.1
        
        # Content depth scoring
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) > 15:
            quality_score += 0.1
        
        # Technical content scoring
        tech_terms = ['research', 'study', 'analysis', 'method', 'algorithm', 'implementation', 
                     'experiment', 'results', 'conclusion', 'approach', 'framework', 'model']
        tech_count = sum(1 for term in tech_terms if term.lower() in text.lower())
        if tech_count > 5:
            quality_score += 0.2
        elif tech_count > 2:
            quality_score += 0.1
        
        # Domain reputation scoring
        domain = urlparse(url).netloc.lower()
        if any(d in domain for d in ['arxiv', 'ieee', 'acm', 'springer', 'nature', 'science']):
            quality_score += 0.3  # Academic sources
        elif any(d in domain for d in ['github', 'stackoverflow', 'medium', 'towards']):
            quality_score += 0.2  # Technical sources
        elif any(d in domain for d in ['wikipedia', 'edu']):
            quality_score += 0.15  # Educational sources
        
        # Structure scoring
        if re.search(r'\b(abstract|introduction|methodology|results|conclusion)\b', text, re.IGNORECASE):
            quality_score += 0.1
        
        quality_score = min(1.0, quality_score)
        
        # Categorize quality
        if quality_score >= 0.8:
            quality = "high"
        elif quality_score >= 0.6:
            quality = "medium"
        else:
            quality = "low"
        
        return quality, round(quality_score, 2)
    
    def _structure_content_as_json(self, text: str, url: str, title: str = "") -> Dict[str, Any]:
        """Structure extracted content into organized JSON format"""
        # Clean the text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Extract title if not provided
        if not title:
            lines = text.split('\n')
            for line in lines[:5]:
                line = line.strip()
                if line and len(line) < 200 and (line.isupper() or not line.endswith('.')):
                    title = line
                    break
            if not title:
                title = text[:100] + "..."
        
        # Split into sections
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        # Create sections based on content
        sections = {}
        text_lower = text.lower()
        
        section_keywords = {
            'abstract': ['abstract', 'summary'],
            'introduction': ['introduction', 'background', 'overview'],
            'methodology': ['method', 'approach', 'algorithm', 'implementation'],
            'results': ['results', 'findings', 'evaluation', 'performance'],
            'conclusion': ['conclusion', 'summary', 'discussion']
        }
        
        for section_name, keywords in section_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    keyword_pos = text_lower.find(keyword)
                    section_start = max(0, keyword_pos - 100)
                    section_end = min(len(text), keyword_pos + 500)
                    section_content = text[section_start:section_end].strip()
                    if len(section_content) > 100:
                        sections[section_name] = section_content
                        break
        
        # If no sections found, create logical chunks
        if not sections:
            chunk_size = len(text) // 3
            if chunk_size > 200:
                sections['part_1'] = text[:chunk_size].strip()
                sections['part_2'] = text[chunk_size:chunk_size*2].strip()
                sections['part_3'] = text[chunk_size*2:].strip()
            else:
                sections['main_content'] = text
        
        # Determine content quality
        quality, quality_score = self._determine_content_quality(text, url)
        
        # Determine content type
        domain = urlparse(url).netloc.lower()
        if any(d in domain for d in ['arxiv', 'ieee', 'acm', 'springer', 'nature']):
            content_type = "academic"
        elif any(d in domain for d in ['github', 'stackoverflow', 'medium']):
            content_type = "technical"
        elif any(d in domain for d in ['news', 'blog', 'post']):
            content_type = "news"
        else:
            content_type = "article"
        
        # Create structured JSON
        structured_content = {
            "metadata": {
                "url": url,
                "title": title,
                "domain": urlparse(url).netloc,
                "extraction_date": datetime.now().isoformat(),
                "content_quality": quality,
                "quality_score": quality_score,
                "content_type": content_type
            },
            "content": {
                "title": title,
                "summary": text[:500] + "..." if len(text) > 500 else text,
                "full_text": text,
                "sections": sections,
                "word_count": len(text.split()),
                "sentence_count": len(sentences),
                "sentences": sentences[:20],  # Limit for storage efficiency
                "character_count": len(text)
            },
            "embedding_metadata": {
                "content_type": content_type,
                "relevance_score": quality_score,
                "language": "en",
                "source_type": "web",
                "processing_version": "2.0",
                "extraction_method": "trafilatura"
            }
        }
        
        return structured_content
    
    def extract_content_from_urls(self, urls: List[str], content_dir: str, metadata_dir: str) -> List[Dict[str, Any]]:
        """Extract clean text content from URLs and store with quality categorization"""
        extracted_content = []
        
        # Ensure directories exist
        os.makedirs(content_dir, exist_ok=True)
        os.makedirs(metadata_dir, exist_ok=True)
        
        logger.info(f"Extracting content from {len(urls)} URLs...")
        
        for i, url in enumerate(urls, 1):
            try:
                domain = urlparse(url).netloc
                logger.info(f"Processing {i}/{len(urls)}: {domain}")
                
                # Generate unique identifier
                url_hash = hashlib.md5(url.encode()).hexdigest()
                content_file = os.path.join(content_dir, f"{url_hash}.json")
                metadata_file = os.path.join(metadata_dir, f"{url_hash}.json")
                
                # Check if already extracted
                if os.path.exists(content_file) and os.path.exists(metadata_file):
                    # Load cached content
                    with open(content_file, 'r', encoding='utf-8') as f:
                        structured_content = json.load(f)
                    
                    extracted_content.append({
                        'url': url,
                        'content': structured_content['content']['full_text'],
                        'structured_content': structured_content,
                        'quality': structured_content['metadata']['content_quality'],
                        'quality_score': structured_content['metadata']['quality_score'],
                        'length': structured_content['content']['word_count'],
                        'content_file': content_file,
                        'metadata_file': metadata_file,
                        'cached': True
                    })
                    continue
                
                # Download and extract content
                if trafilatura:
                    downloaded = trafilatura.fetch_url(url)
                    
                    if downloaded:
                        # Extract with maximum content settings
                        text = trafilatura.extract(
                            downloaded,
                            include_comments=False,
                            include_tables=True,
                            include_formatting=True,
                            include_links=False,
                            favor_precision=False,
                            favor_recall=True,
                            output_format='txt'
                        )
                        
                        # Try fallback extraction if needed
                        if not text or len(text) < 200:
                            text = trafilatura.extract(
                                downloaded,
                                include_comments=True,
                                include_tables=True,
                                favor_precision=True,
                                output_format='txt'
                            )
                        
                        if text and len(text) > 100:
                            # Structure content with quality assessment
                            structured_content = self._structure_content_as_json(text, url)
                            
                            # Save structured content
                            with open(content_file, 'w', encoding='utf-8') as f:
                                json.dump(structured_content, f, indent=2, ensure_ascii=False)
                            
                            # Save metadata separately
                            metadata = {
                                'url': url,
                                'extraction_date': datetime.now().isoformat(),
                                'content_quality': structured_content['metadata']['content_quality'],
                                'quality_score': structured_content['metadata']['quality_score'],
                                'word_count': structured_content['content']['word_count'],
                                'content_type': structured_content['metadata']['content_type'],
                                'domain': structured_content['metadata']['domain'],
                                'title': structured_content['metadata']['title']
                            }
                            
                            with open(metadata_file, 'w', encoding='utf-8') as f:
                                json.dump(metadata, f, indent=2, ensure_ascii=False)
                            
                            extracted_content.append({
                                'url': url,
                                'content': text,
                                'structured_content': structured_content,
                                'quality': structured_content['metadata']['content_quality'],
                                'quality_score': structured_content['metadata']['quality_score'],
                                'length': len(text.split()),
                                'content_file': content_file,
                                'metadata_file': metadata_file,
                                'cached': False
                            })
                            
                            quality = structured_content['metadata']['content_quality']
                            logger.info(f"Extracted {len(text.split())} words | Quality: {quality}")
                        else:
                            logger.warning(f"Insufficient content extracted from {domain}")
                    else:
                        logger.warning(f"Failed to download content from {domain}")
                else:
                    logger.warning("Trafilatura not available - content extraction disabled")
                    
            except Exception as e:
                logger.warning(f"Error extracting from {url}: {str(e)}")
                continue
        
        # Log extraction summary
        if extracted_content:
            quality_counts = {}
            for item in extracted_content:
                quality = item.get('quality', 'unknown')
                quality_counts[quality] = quality_counts.get(quality, 0) + 1
            
            logger.info(f"Content quality distribution: {quality_counts}")
        
        logger.info(f"Successfully extracted {len(extracted_content)}/{len(urls)} web contents")
        return extracted_content
    
    def search_and_extract_for_chunks(self, chunks: List[str], web_content_dir: str, max_results_per_chunk: int = 2) -> Dict[str, Any]:
        """
        Search and extract web content for multiple text chunks
        
        Args:
            chunks: List of text chunks to search for
            web_content_dir: Directory to store web content
            max_results_per_chunk: Maximum results per chunk
        
        Returns:
            Dictionary with search results and extraction summary
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Tavily service not available',
                'results': []
            }
        
        # Create subdirectories
        content_dir = os.path.join(web_content_dir, 'content')
        metadata_dir = os.path.join(web_content_dir, 'metadata')
        os.makedirs(content_dir, exist_ok=True)
        os.makedirs(metadata_dir, exist_ok=True)
        
        all_search_results = []
        all_extracted_content = []
        seen_urls = set()
        
        logger.info(f"Processing {len(chunks)} chunks for web search")
        
        # Limit chunks to avoid overwhelming the API
        selected_chunks = chunks[:8] if len(chunks) > 8 else chunks
        
        for i, chunk in enumerate(selected_chunks, 1):
            if len(chunk.strip()) < 50:  # Skip very short chunks
                continue
            
            logger.info(f"Processing chunk {i}/{len(selected_chunks)} ({len(chunk)} chars)")
            
            try:
                # Search for this chunk
                search_results = self.search_web(chunk, max_results_per_chunk)
                
                if search_results:
                    # Filter out duplicate URLs
                    new_urls = []
                    for result in search_results:
                        url = result.get('url')
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            new_urls.append(url)
                            result['source_chunk'] = i
                            all_search_results.append(result)
                    
                    # Extract content from new URLs
                    if new_urls:
                        extracted = self.extract_content_from_urls(new_urls, content_dir, metadata_dir)
                        all_extracted_content.extend(extracted)
                
            except Exception as e:
                logger.error(f"Error processing chunk {i}: {str(e)}")
                continue
        
        # Create comprehensive results summary
        quality_distribution = {'high': 0, 'medium': 0, 'low': 0}
        total_word_count = 0
        
        for content in all_extracted_content:
            quality = content.get('quality', 'unknown')
            if quality in quality_distribution:
                quality_distribution[quality] += 1
            total_word_count += content.get('length', 0)
        
        # Save web results summary
        results_summary = {
            'search_metadata': {
                'chunks_processed': len(selected_chunks),
                'total_searches': len(selected_chunks),
                'unique_urls_found': len(seen_urls),
                'content_extracted': len(all_extracted_content),
                'extraction_date': datetime.now().isoformat()
            },
            'content_summary': {
                'total_word_count': total_word_count,
                'quality_distribution': quality_distribution,
                'average_content_length': total_word_count // len(all_extracted_content) if all_extracted_content else 0
            },
            'search_results': all_search_results,
            'extracted_content': [
                {
                    'url': item['url'],
                    'quality': item['quality'],
                    'quality_score': item['quality_score'],
                    'word_count': item['length'],
                    'cached': item['cached'],
                    'content_file': os.path.basename(item['content_file']),
                    'metadata_file': os.path.basename(item['metadata_file'])
                }
                for item in all_extracted_content
            ]
        }
        
        # Save results summary
        summary_file = os.path.join(web_content_dir, 'web_results.json')
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results_summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved web results summary: {summary_file}")
        
        return {
            'success': True,
            'chunks_processed': len(selected_chunks),
            'urls_found': len(seen_urls),
            'content_extracted': len(all_extracted_content),
            'quality_distribution': quality_distribution,
            'total_word_count': total_word_count,
            'storage_path': web_content_dir,
            'summary_file': summary_file,
            'results': results_summary
        }