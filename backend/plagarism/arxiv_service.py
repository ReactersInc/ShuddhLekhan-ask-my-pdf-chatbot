"""
ArXiv Service for Plagiarism Checker
"""

import os
import time
import json
import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import Counter
import re


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class ArxivService:
    def __init__(self):
        # API configuration
        self.base_url = "http://export.arxiv.org/api/query"
        self.rate_limit = 3  # seconds between requests
        self.session = requests.Session()
        
        # Configure session headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Set up directory structure
        self.base_dir = "./scraped_data"
        self.arxiv_dir = os.path.join(self.base_dir, "arxiv")
        self.pdfs_dir = os.path.join(self.arxiv_dir, "pdfs")
        self.metadata_dir = os.path.join(self.arxiv_dir, "metadata")
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories for file storage"""
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.arxiv_dir, exist_ok=True)
        os.makedirs(self.pdfs_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
    
    def _clean_query(self, query: str) -> str:
        """Clean and format query for arXiv API"""
        query = query.strip()
        # Remove quotes and special characters that might break API
        query = query.replace('"', '').replace("'", "")
        # Normalize whitespace
        query = ' '.join(query.split())
        # Limit query length for API compatibility
        if len(query) > 200:
            query = query[:200]
        return query
    
    def search_papers(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for papers using multiple search strategies"""
        try:
            # Clean the query
            query = self._clean_query(query)
            
            # Multiple search strategies for better coverage
            search_strategies = [
                f'all:{query}',  # Search all fields
                f'ti:{query}',   # Search titles only
                f'abs:{query}',  # Search abstracts only
            ]
            
            all_papers = []
            seen_ids = set()
            
            # Try each strategy
            for strategy in search_strategies:
                params = {
                    'search_query': strategy,
                    'start': 0,
                    'max_results': min(max_results, 15),
                    'sortBy': 'relevance',
                    'sortOrder': 'descending'
                }
                
                try:
                    # Make API request
                    response = self.session.get(self.base_url, params=params, timeout=30)
                    response.raise_for_status()
                    
                    # Parse response
                    papers = self._parse_arxiv_response(response.text)
                    
                    # Add unique papers only
                    for paper in papers:
                        arxiv_id = paper.get('arxiv_id')
                        if arxiv_id and arxiv_id not in seen_ids:
                            seen_ids.add(arxiv_id)
                            all_papers.append(paper)
                    
                    # Rate limiting
                    time.sleep(self.rate_limit)
                    
                except Exception as e:
                    logger.warning(f"Search strategy failed: {str(e)}")
                    continue
            
            # Score papers by relevance
            scored_papers = self._score_paper_relevance(all_papers, query)
            
            # Return top results
            final_papers = scored_papers[:max_results]
            
            return final_papers
            
        except Exception as e:
            logger.error(f"ArXiv search error: {str(e)}")
            return []
    
    def _score_paper_relevance(self, papers: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Score papers by relevance to search query"""
        try:
            # Extract query terms for scoring
            query_terms = re.findall(r'\b\w{3,}\b', query.lower())
            query_words = set(query_terms)
            
            scored_papers = []
            
            for paper in papers:
                score = 0
                
                # Get paper text - ensure strings
                title = str(paper.get('title', '')) if paper.get('title') else ""
                abstract = str(paper.get('abstract', '')) if paper.get('abstract') else ""
                
                title = title.lower()
                abstract = abstract.lower()
                
                # Title matches get high score
                title_words = set(re.findall(r'\b\w{3,}\b', title))
                title_matches = len(title_words.intersection(query_words))
                score += title_matches * 10
                
                # Abstract matches get medium score
                abstract_words = set(re.findall(r'\b\w{3,}\b', abstract))
                abstract_matches = len(abstract_words.intersection(query_words))
                score += abstract_matches * 3
                
                # Phrase matching bonus
                for term in query_terms:
                    if len(term) > 4:
                        if term in title:
                            score += 15  # High bonus for title phrase match
                        elif term in abstract:
                            score += 5   # Medium bonus for abstract phrase match
                
                # Recent papers get slight bonus
                try:
                    published = paper.get('published', '')
                    if published and ('2023' in published or '2024' in published or '2025' in published):
                        score += 2
                except:
                    pass
                
                # Store score with paper
                paper_with_score = paper.copy()
                paper_with_score['relevance_score'] = score
                scored_papers.append(paper_with_score)
            
            # Sort by score descending
            scored_papers.sort(key=lambda p: p.get('relevance_score', 0), reverse=True)
            
            return scored_papers
            
        except Exception as e:
            logger.error(f"Error scoring papers: {str(e)}")
            return papers
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse arXiv API XML response into paper data"""
        try:
            papers = []
            root = ET.fromstring(xml_content)
            
            # Define XML namespaces
            namespace = {'atom': 'http://www.w3.org/2005/Atom',
                        'arxiv': 'http://arxiv.org/schemas/atom'}
            
            # Process each paper entry
            entries = root.findall('.//atom:entry', namespace)
            
            for entry in entries:
                paper = {}
                
                # Extract title
                title_elem = entry.find('atom:title', namespace)
                paper['title'] = title_elem.text.strip() if title_elem is not None else ""
                
                # Extract abstract
                summary_elem = entry.find('atom:summary', namespace)
                paper['abstract'] = summary_elem.text.strip() if summary_elem is not None else ""
                
                # Extract authors
                authors = []
                author_elems = entry.findall('atom:author/atom:name', namespace)
                for author_elem in author_elems:
                    authors.append(author_elem.text.strip())
                paper['authors'] = authors
                
                # Extract published date
                published_elem = entry.find('atom:published', namespace)
                paper['published'] = published_elem.text.strip() if published_elem is not None else ""
                
                # Extract arXiv ID from URL
                id_elem = entry.find('atom:id', namespace)
                if id_elem is not None:
                    paper['arxiv_id'] = id_elem.text.split('/')[-1]
                    paper['url'] = id_elem.text
                
                # Extract PDF link
                links = entry.findall('atom:link', namespace)
                for link in links:
                    if link.get('title') == 'pdf':
                        paper['pdf_url'] = link.get('href')
                        break
                
                # Construct PDF URL if not found
                if 'pdf_url' not in paper and 'arxiv_id' in paper:
                    paper['pdf_url'] = f"https://arxiv.org/pdf/{paper['arxiv_id']}.pdf"
                
                # Extract categories
                categories = []
                category_elems = entry.findall('atom:category', namespace)
                for cat_elem in category_elems:
                    categories.append(cat_elem.get('term', ''))
                paper['categories'] = categories
                
                # Only include papers with title and abstract
                if paper.get('title') and paper.get('abstract'):
                    papers.append(paper)
            
            return papers
            
        except ET.ParseError as e:
            logger.error(f"Error parsing arXiv XML: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected parsing error: {str(e)}")
            return []
    
    def download_paper_pdf(self, paper: Dict[str, Any]) -> Optional[str]:
        """Download PDF file for a paper"""
        try:
            arxiv_id = paper.get('arxiv_id', '')
            title = paper.get('title', 'Unknown')
            pdf_url = paper.get('pdf_url', '')
            
            if not arxiv_id or not pdf_url:
                return None
            
            # Create file paths
            safe_filename = f"{arxiv_id}.pdf"
            pdf_path = os.path.join(self.pdfs_dir, safe_filename)
            metadata_path = os.path.join(self.metadata_dir, f"{arxiv_id}.json")
            
            # Check if already downloaded
            if os.path.exists(pdf_path):
                return pdf_path
            
            # Download PDF
            response = self.session.get(pdf_url, timeout=60)
            response.raise_for_status()
            
            # Validate PDF content
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and len(response.content) < 1000:
                return None
            
            # Save PDF file
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            # Save metadata
            metadata = {
                'arxiv_id': arxiv_id,
                'title': paper.get('title', ''),
                'abstract': paper.get('abstract', ''),
                'authors': paper.get('authors', []),
                'published': paper.get('published', ''),
                'categories': paper.get('categories', []),
                'pdf_url': pdf_url,
                'url': paper.get('url', ''),
                'download_date': datetime.now().isoformat(),
                'pdf_path': pdf_path,
                'file_size': os.path.getsize(pdf_path),
                'relevance_score': paper.get('relevance_score', 0)
            }
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Rate limiting
            time.sleep(self.rate_limit)
            
            return pdf_path
            
        except requests.RequestException as e:
            logger.error(f"Failed to download PDF for {arxiv_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error downloading PDF: {e}")
            return None
    
    def search_and_download_from_keywords(self, keywords_json_path: str, max_papers: int = 5) -> Dict[str, Any]:
        """
        Search and download papers based on keywords from JSON file
        
        Args:
            keywords_json_path: Path to keywords.json file
            max_papers: Maximum number of papers to download
        
        Returns:
            Dictionary with search results and download status
        """
        try:
            # Load keywords from file
            with open(keywords_json_path, 'r', encoding='utf-8') as f:
                keywords_data = json.load(f)
            
            # Extract meaningful keywords from all sections
            all_keywords = []
            important_phrases = []
            
            for i, section in enumerate(keywords_data):
                try:
                    if isinstance(section, dict) and not section.get('error'):
                        section_name = str(section.get('section', '')).lower()
                        
                        # Get keywords and phrases with type safety
                        section_keywords = section.get('keywords', [])
                        section_phrases = section.get('key_phrases', [])
                        
                        # Filter out metadata terms - ensure string conversion
                        filtered_keywords = []
                        for kw in section_keywords:
                            try:
                                if kw is not None:
                                    kw_str = str(kw).strip()
                                    if len(kw_str) > 2:
                                        # Skip metadata terms
                                        if not any(meta in kw_str.lower() for meta in 
                                                  ['arxiv', 'v1', 'v2', 'v3', '2025', '2024', '2023', 'preprint', 'hep-ex']):
                                            filtered_keywords.append(kw_str)
                            except Exception:
                                continue
                        
                        filtered_phrases = []
                        for phrase in section_phrases:
                            try:
                                if phrase is not None:
                                    phrase_str = str(phrase).strip()
                                    if len(phrase_str) > 4:
                                        # Skip metadata terms
                                        if not any(meta in phrase_str.lower() for meta in 
                                                  ['arxiv', 'v1', 'v2', 'submitted', 'preprint']):
                                            filtered_phrases.append(phrase_str)
                            except Exception:
                                continue
                        
                        all_keywords.extend(filtered_keywords)
                        important_phrases.extend(filtered_phrases)
                        
                except Exception:
                    continue
            
            # Get unique terms
            unique_keywords = list(set(all_keywords))
            unique_phrases = list(set(important_phrases))
            
            if not (unique_keywords or unique_phrases):
                return {
                    'success': False,
                    'error': 'No meaningful keywords found',
                    'papers_found': 0,
                    'papers_downloaded': 0
                }
            
            # Create search queries
            search_queries = []
            
            # Primary: phrases + keywords
            if unique_phrases and unique_keywords:
                primary_query = f"{' '.join(unique_phrases[:2])} {' '.join(unique_keywords[:3])}"
                search_queries.append(primary_query)
            
            # Secondary: keywords only
            if unique_keywords:
                secondary_query = ' '.join(unique_keywords[:5])
                search_queries.append(secondary_query)
            
            # Tertiary: phrases only
            if unique_phrases:
                tertiary_query = ' '.join(unique_phrases[:3])
                search_queries.append(tertiary_query)
            
            # Search with multiple queries
            all_papers = []
            seen_ids = set()
            final_query = ""
            
            for i, query in enumerate(search_queries):
                papers = self.search_papers(query, max_papers * 2)
                
                # Add unique papers
                new_papers = 0
                for paper in papers:
                    arxiv_id = paper.get('arxiv_id')
                    if arxiv_id and arxiv_id not in seen_ids:
                        seen_ids.add(arxiv_id)
                        all_papers.append(paper)
                        new_papers += 1
                
                # Use first successful query
                if not final_query and papers:
                    final_query = query
                
                # Stop if enough papers found
                if len(all_papers) >= max_papers * 1.5:
                    break
            
            if not all_papers:
                return {
                    'success': False,
                    'error': 'No papers found for keywords',
                    'papers_found': 0,
                    'papers_downloaded': 0
                }
            
            # Select top papers by relevance
            top_papers = all_papers[:max_papers]
            
            # Download selected papers
            download_results = []
            download_count = 0
            
            for paper in top_papers:
                try:
                    pdf_path = self.download_paper_pdf(paper)
                    
                    result = {
                        'arxiv_id': paper.get('arxiv_id'),
                        'title': paper.get('title'),
                        'relevance_score': paper.get('relevance_score', 0),
                        'published_year': paper.get('published', '')[:4] if paper.get('published') else 'Unknown',
                        'download_success': pdf_path is not None,
                        'pdf_path': pdf_path,
                        'error': None
                    }
                    
                    if pdf_path:
                        download_count += 1
                    else:
                        result['error'] = 'Download failed'
                    
                    download_results.append(result)
                    
                except Exception as e:
                    download_results.append({
                        'arxiv_id': paper.get('arxiv_id'),
                        'title': paper.get('title'),
                        'download_success': False,
                        'error': str(e)
                    })
            
            # Save results summary
            results_summary = {
                'search_metadata': {
                    'final_query': final_query,
                    'keywords_extracted': len(unique_keywords),
                    'phrases_extracted': len(unique_phrases),
                    'search_strategies': len(search_queries),
                    'search_date': datetime.now().isoformat()
                },
                'papers_found': len(all_papers),
                'papers_downloaded': download_count,
                'papers_failed': len(top_papers) - download_count,
                'download_results': download_results,
                'storage_paths': {
                    'base_dir': self.base_dir,
                    'arxiv_dir': self.arxiv_dir,
                    'pdfs_dir': self.pdfs_dir,
                    'metadata_dir': self.metadata_dir
                }
            }
            
            # Save results to file
            results_file = os.path.join(self.arxiv_dir, 'arxiv_results.json')
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results_summary, f, indent=2, ensure_ascii=False)
            
            return {
                'success': download_count > 0,
                'query': final_query,
                'keywords_used': unique_keywords[:5],
                'phrases_used': unique_phrases[:3],
                'papers_found': len(all_papers),
                'papers_downloaded': download_count,
                'papers_failed': len(top_papers) - download_count,
                'storage_paths': results_summary['storage_paths'],
                'results_file': results_file,
                'download_results': download_results
            }
            
        except Exception as e:
            logger.error(f"Error in search and download: {e}")
            return {
                'success': False,
                'error': str(e),
                'papers_found': 0,
                'papers_downloaded': 0
            }

if __name__ == "__main__":
    # Test the service
    service = ArxivService()
    
    # Test search functionality
    papers = service.search_papers("dark matter neutron detection", max_results=3)
    print(f"Found {len(papers)} papers")
    
    for paper in papers:
        score = paper.get('relevance_score', 0)
        print(f"- Score: {score} | {paper['arxiv_id']}: {paper['title'][:60]}...")
