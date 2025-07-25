import re
import math
from typing import Dict, List
from collections import Counter

class ChunkComplexityAnalyzer:
    """
    Analyzes text chunks to determine complexity, language, and optimal API routing
    """
    
    def __init__(self):
        # Technical keywords for complexity detection
        self.technical_keywords = {
            'algorithm', 'method', 'analysis', 'research', 'study', 'theory',
            'implementation', 'framework', 'model', 'system', 'approach',
            'technique', 'process', 'evaluation', 'experimental', 'optimization',
            'database', 'network', 'protocol', 'architecture', 'design',
            'mathematics', 'equation', 'formula', 'calculation', 'statistics',
            'machine learning', 'artificial intelligence', 'deep learning',
            'neural network', 'data science', 'programming', 'software'
        }
        
        # Hindi/Urdu/Bengali script detection patterns
        self.indic_scripts = {
            'hindi': re.compile(r'[\u0900-\u097F]'),  # Devanagari
            'urdu': re.compile(r'[\u0600-\u06FF]'),   # Arabic/Urdu
            'bengali': re.compile(r'[\u0980-\u09FF]'), # Bengali
            'krutidev': re.compile(r'[a-zA-Z]{2,}')    # Krutidev detection (Roman chars for Hindi)
        }
        
        # Mathematical patterns
        self.math_patterns = [
            re.compile(r'\d+\s*[+\-*/=]\s*\d+'),      # Basic math operations
            re.compile(r'[a-zA-Z]\s*=\s*\d+'),         # Variable assignments
            re.compile(r'∫|∑|∏|√|∆|∇|∂'),              # Mathematical symbols
            re.compile(r'\b(sin|cos|tan|log|ln)\b'),   # Mathematical functions
        ]
    
    def analyze_chunk(self, chunk: str) -> Dict:
        """
        Analyze chunk and return comprehensive analysis
        """
        try:
            # Basic text analysis
            word_count = len(chunk.split())
            char_count = len(chunk)
            sentence_count = len([s for s in chunk.split('.') if s.strip()])
            avg_word_length = sum(len(word) for word in chunk.split()) / max(word_count, 1)
            
            # Language detection
            language_info = self._detect_language(chunk)
            
            # Technical complexity
            technical_score = self._calculate_technical_score(chunk)
            
            # Mathematical content
            math_score = self._calculate_math_score(chunk)
            
            # Overall complexity calculation
            complexity_score = self._calculate_complexity_score(
                word_count, technical_score, math_score, avg_word_length
            )
            
            # Determine complexity level
            if complexity_score >= 7:
                complexity = "complex"
            elif complexity_score >= 4:
                complexity = "medium"
            else:
                complexity = "simple"
            
            # Determine routing priority
            priority = self._determine_priority(language_info, complexity, technical_score)
            
            return {
                "complexity": complexity,
                "complexity_score": round(complexity_score, 2),
                "language": language_info["primary_language"],
                "language_confidence": language_info["confidence"],
                "has_indic_script": language_info["has_indic_script"],
                "priority": priority,
                "technical_score": technical_score,
                "math_score": math_score,
                "word_count": word_count,
                "char_count": char_count,
                "avg_word_length": round(avg_word_length, 2),
                "recommended_api": self._recommend_api(language_info, complexity, priority)
            }
            
        except Exception as e:
            # Fallback analysis in case of errors
            return {
                "complexity": "medium",
                "complexity_score": 5.0,
                "language": "en",
                "language_confidence": 0.5,
                "has_indic_script": False,
                "priority": "medium",
                "technical_score": 3,
                "math_score": 1,
                "word_count": len(chunk.split()),
                "char_count": len(chunk),
                "avg_word_length": 5.0,
                "recommended_api": "google_primary",
                "error": str(e)
            }
    
    def _detect_language(self, text: str) -> Dict:
        """Detect language and script type"""
        # Check for Indic scripts
        indic_matches = {}
        for script, pattern in self.indic_scripts.items():
            matches = len(pattern.findall(text))
            if matches > 0:
                indic_matches[script] = matches
        
        # Determine primary language
        if indic_matches:
            # Has Indic script content
            primary_script = max(indic_matches, key=indic_matches.get)
            confidence = min(indic_matches[primary_script] / len(text.split()) * 10, 1.0)
            
            return {
                "primary_language": primary_script,
                "confidence": round(confidence, 2),
                "has_indic_script": True,
                "indic_matches": indic_matches
            }
        else:
            # Assume English
            return {
                "primary_language": "en",
                "confidence": 0.8,
                "has_indic_script": False,
                "indic_matches": {}
            }
    
    def _calculate_technical_score(self, text: str) -> int:
        """Calculate technical complexity score (0-10)"""
        text_lower = text.lower()
        technical_count = sum(1 for keyword in self.technical_keywords if keyword in text_lower)
        
        # Normalize to 0-10 scale
        return min(technical_count, 10)
    
    def _calculate_math_score(self, text: str) -> int:
        """Calculate mathematical content score (0-5)"""
        math_count = sum(len(pattern.findall(text)) for pattern in self.math_patterns)
        return min(math_count, 5)
    
    def _calculate_complexity_score(self, word_count: int, technical_score: int, 
                                  math_score: int, avg_word_length: float) -> float:
        """Calculate overall complexity score (0-10)"""
        # Word count factor (0-3)
        word_factor = min(word_count / 200, 3)
        
        # Technical factor (0-4)
        technical_factor = technical_score * 0.4
        
        # Math factor (0-2)
        math_factor = math_score * 0.4
        
        # Word length factor (0-1)
        length_factor = min((avg_word_length - 4) * 0.2, 1) if avg_word_length > 4 else 0
        
        total_score = word_factor + technical_factor + math_factor + length_factor
        return min(total_score, 10)
    
    def _determine_priority(self, language_info: Dict, complexity: str, technical_score: int) -> str:
        """Determine routing priority"""
        if language_info["has_indic_script"]:
            return "critical"  # Must use Google Gemma
        elif complexity == "complex" or technical_score >= 7:
            return "high"      # Prefer Google Gemma
        elif complexity == "medium":
            return "medium"    # Can use any good API
        else:
            return "low"       # Can use any available API
    
    def _recommend_api(self, language_info: Dict, complexity: str, priority: str) -> str:
        """Recommend best API based on analysis"""
        if language_info["has_indic_script"]:
            return "google_primary"  # Only Google can handle Indic scripts well
        elif priority == "high":
            return "google_primary"  # Use best model for complex content
        elif priority == "medium":
            return "google_balanced"  # Can distribute between Google APIs
        else:
            return "any_available"   # Can use any API including fallbacks
    
    def analyze_batch(self, chunks: List[str]) -> List[Dict]:
        """Analyze multiple chunks efficiently"""
        return [self.analyze_chunk(chunk) for chunk in chunks]
