import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass

@dataclass
class APIUsageStats:
    """Track API usage statistics"""
    calls_made: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    last_call_time: float = 0
    last_error: Optional[str] = None
    is_available: bool = True
    rate_limit_reset_time: float = 0  # When rate limit will reset
    consecutive_failures: int = 0

class SmartAPIManager:
    """
    Reactive API manager that switches APIs only when rate limits are actually hit
    """
    
    def __init__(self):
        # API configurations - NO HARDCODED LIMITS!
        self.api_configs = {
            'google_primary': {
                'key': os.getenv('GOOGLE_API_KEY'),
                'delay_between_calls': 4,  # 15 RPM = 4 seconds between calls
                'model': 'gemini-1.5-flash',
                'priority': 1,
                'supports_indic': True,
                'provider': 'google'
            },
            'google_secondary': {
                'key': os.getenv('GOOGLE_API_KEY_2'),
                'delay_between_calls': 4,  # 15 RPM = 4 seconds between calls
                'model': 'gemini-1.5-flash',
                'priority': 2,
                'supports_indic': True,
                'provider': 'google'
            },
            'groq': {
                'key': os.getenv('GROQ_API_KEY'),
                'delay_between_calls': 1,  # GROQ is usually faster
                'model': 'llama-3.1-8b-instant',
                'priority': 3,
                'supports_indic': False,
                'provider': 'groq'
            },
            'together_ai': {
                'key': os.getenv('TOGETHER_AI_API_KEY'),
                'delay_between_calls': 2,  # Conservative for Together AI
                'model': 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo',
                'priority': 4,
                'supports_indic': False,
                'provider': 'together'
            },
            'openrouter': {
                'key': os.getenv('OPENROUTER_API_KEY'),
                'delay_between_calls': 3,  # Conservative for OpenRouter free tier
                'model': 'meta-llama/llama-3.1-8b-instruct:free',
                'priority': 5,
                'supports_indic': False,
                'provider': 'openrouter'
            }
        }
        
        # Initialize usage tracking
        self.usage_stats = {}
        self._initialize_usage_stats()
        
        # Google APIs are our primary preference
        self.google_apis = ['google_primary', 'google_secondary']
        self.fallback_apis = ['groq', 'together_ai', 'openrouter']
        
        available_count = len([k for k, v in self.api_configs.items() if v['key']])
        print(f"🔧 Smart API Manager initialized with {available_count} available APIs")
    
    def _initialize_usage_stats(self):
        """Initialize usage statistics"""
        for api_name in self.api_configs.keys():
            if api_name not in self.usage_stats:
                self.usage_stats[api_name] = APIUsageStats()
    
    def get_priority_api_sequence(self, chunk_analysis: Dict) -> List[str]:
        """
        Get API sequence based on priority and chunk analysis
        """
        has_indic_script = chunk_analysis.get("has_indic_script", False)
        complexity = chunk_analysis.get("complexity", "medium")
        
        # RULE 1: Indic content MUST use Google APIs only
        if has_indic_script:
            available_google = [api for api in self.google_apis 
                               if self.api_configs[api]['key'] and self._is_api_currently_available(api)]
            if not available_google:
                print("⚠️ WARNING: No Google APIs available for Indic content!")
                return []
            return available_google
        
        # RULE 2: Always prefer Google APIs first (primary, then secondary)
        api_sequence = []
        
        # Add available Google APIs first
        for api in self.google_apis:
            if self.api_configs[api]['key'] and self._is_api_currently_available(api):
                api_sequence.append(api)
        
        # Add fallback APIs based on complexity
        if complexity == "complex":
            # For complex content, prefer powerful models
            fallback_order = ['together_ai', 'groq', 'openrouter']
        else:
            # For simple content, prefer faster models
            fallback_order = ['groq', 'together_ai', 'openrouter']
        
        for api in fallback_order:
            if self.api_configs[api]['key'] and self._is_api_currently_available(api):
                api_sequence.append(api)
        
        return api_sequence
    
    def _is_api_currently_available(self, api_name: str) -> bool:
        """Check if API is currently available (not in rate limit cooldown)"""
        if api_name not in self.usage_stats:
            return True
            
        stats = self.usage_stats[api_name]
        current_time = time.time()
        
        # Check if API is marked as unavailable due to rate limits
        if not stats.is_available:
            # Check if rate limit cooldown period has passed
            if current_time >= stats.rate_limit_reset_time:
                print(f"🔄 Rate limit cooldown expired for {api_name}, re-enabling")
                stats.is_available = True
                stats.consecutive_failures = 0
                return True
            else:
                cooldown_remaining = int(stats.rate_limit_reset_time - current_time)
                print(f"⏳ {api_name} still in rate limit cooldown ({cooldown_remaining}s remaining)")
                return False
        
        return True
    
    def record_api_call(self, api_name: str, success: bool, error_message: str = None):
        """Record API call and handle rate limit detection"""
        if api_name not in self.usage_stats:
            self._initialize_usage_stats()
        
        stats = self.usage_stats[api_name]
        stats.calls_made += 1
        stats.last_call_time = time.time()
        
        if success:
            stats.successful_calls += 1
            stats.consecutive_failures = 0
            stats.last_error = None
            # Ensure API is marked as available after success
            stats.is_available = True
            
        else:
            stats.failed_calls += 1
            stats.consecutive_failures += 1
            stats.last_error = error_message
            
            if error_message:
                self._handle_api_error(api_name, error_message)
    
    def _handle_api_error(self, api_name: str, error_message: str):
        """Handle different types of API errors reactively"""
        error_lower = error_message.lower()
        stats = self.usage_stats[api_name]
        current_time = time.time()
        
        # RATE LIMIT ERRORS - This is what we're designed to handle!
        if any(keyword in error_lower for keyword in [
            '429', 'rate limit', 'quota', 'exceeded', 'too many requests',
            'rate_limit_exceeded', 'quota_exceeded', 'limit exceeded'
        ]):
            print(f"🚫 RATE LIMIT detected for {api_name}: {error_message[:100]}...")
            stats.is_available = False
            
            # Extract retry-after from error if available, otherwise use smart defaults
            if 'retry-after' in error_lower:
                # Try to extract retry time from error message
                import re
                retry_match = re.search(r'retry.after.?(\d+)', error_lower)
                if retry_match:
                    retry_seconds = int(retry_match.group(1))
                    stats.rate_limit_reset_time = current_time + retry_seconds + 10  # Add 10s buffer
                else:
                    stats.rate_limit_reset_time = current_time + 300  # 5 minutes default
            else:
                # Smart cooldown based on API provider
                if 'google' in api_name:
                    # Google: 15 RPM limit, so wait for minute reset + buffer
                    stats.rate_limit_reset_time = current_time + 70  # 70 seconds
                elif 'groq' in api_name:
                    # GROQ usually has per-minute limits
                    stats.rate_limit_reset_time = current_time + 90  # 90 seconds
                else:
                    # Other APIs - conservative cooldown
                    stats.rate_limit_reset_time = current_time + 180  # 3 minutes
            
            cooldown_time = int(stats.rate_limit_reset_time - current_time)
            print(f"⏳ {api_name} will be retried in {cooldown_time} seconds")
        
        # AUTHENTICATION ERRORS
        elif any(keyword in error_lower for keyword in [
            'api key', 'authentication', 'unauthorized', '401', '403', 'invalid key'
        ]):
            print(f"🔐 AUTHENTICATION ERROR for {api_name}: {error_message[:100]}...")
            stats.is_available = False
            stats.rate_limit_reset_time = current_time + 3600  # 1 hour cooldown - needs manual fix
        
        # TEMPORARY SERVICE ERRORS
        elif any(keyword in error_lower for keyword in [
            '500', '502', '503', '504', 'timeout', 'connection', 'service unavailable'
        ]):
            print(f"🔧 TEMPORARY ERROR for {api_name}: {error_message[:100]}...")
            stats.is_available = False
            stats.rate_limit_reset_time = current_time + 120  # 2 minutes for service recovery
        
        # TOO MANY CONSECUTIVE FAILURES
        elif stats.consecutive_failures >= 3:
            print(f"❌ TOO MANY FAILURES for {api_name} ({stats.consecutive_failures} consecutive)")
            stats.is_available = False
            stats.rate_limit_reset_time = current_time + 300  # 5 minutes cooldown
        
        else:
            # Unknown error - short cooldown
            print(f"❓ UNKNOWN ERROR for {api_name}: {error_message[:100]}...")
            stats.is_available = False
            stats.rate_limit_reset_time = current_time + 60  # 1 minute cooldown
    
    
    def get_api_delay(self, api_name: str) -> float:
        """Get required delay between calls for specific API"""
        return self.api_configs.get(api_name, {}).get('delay_between_calls', 1)
    
    def get_api_config(self, api_name: str) -> Dict:
        """Get configuration for specific API"""
        return self.api_configs.get(api_name, {})
    
    def get_usage_summary(self) -> Dict:
        """Get comprehensive usage summary without artificial limits"""
        summary = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "api_breakdown": {}
        }
        
        for api_name, stats in self.usage_stats.items():
            config = self.api_configs[api_name]
            
            # Calculate availability status
            is_available = self._is_api_currently_available(api_name)
            cooldown_remaining = 0
            if not is_available and stats.rate_limit_reset_time > time.time():
                cooldown_remaining = int(stats.rate_limit_reset_time - time.time())
            
            api_summary = {
                "calls_made": stats.calls_made,
                "successful_calls": stats.successful_calls,
                "failed_calls": stats.failed_calls,
                "consecutive_failures": stats.consecutive_failures,
                "is_available": is_available,
                "cooldown_remaining_seconds": cooldown_remaining,
                "last_error": stats.last_error,
                "provider": config.get('provider', 'unknown'),
                "priority": config.get('priority', 999)
            }
            summary["api_breakdown"][api_name] = api_summary
            summary["total_calls"] += stats.calls_made
            summary["successful_calls"] += stats.successful_calls
            summary["failed_calls"] += stats.failed_calls
        
        return summary
    
    def emergency_reset(self, api_name: str):
        """Emergency reset for specific API"""
        if api_name in self.usage_stats:
            stats = self.usage_stats[api_name]
            stats.is_available = True
            stats.last_error = None
            stats.consecutive_failures = 0
            stats.rate_limit_reset_time = 0
            print(f"🔄 Emergency reset for {api_name}")
    
    def force_enable_all_apis(self):
        """Force enable all APIs (for testing or emergency)"""
        for api_name in self.usage_stats:
            self.emergency_reset(api_name)
        print("🔄 Force enabled all APIs")
    
    def print_status(self):
        """Print current API status"""
        print("\n� Reactive API Manager Status:")
        print("=" * 55)
        
        current_time = time.time()
        
        for api_name, config in self.api_configs.items():
            if not config['key']:
                print(f"❌ {api_name}: No API key")
                continue
            
            stats = self.usage_stats[api_name]
            is_available = self._is_api_currently_available(api_name)
            
            if is_available:
                status = "🟢 READY"
            else:
                cooldown_remaining = int(stats.rate_limit_reset_time - current_time)
                status = f"🔴 COOLDOWN ({cooldown_remaining}s)"
            
            # Show call statistics
            success_rate = 0
            if stats.calls_made > 0:
                success_rate = round((stats.successful_calls / stats.calls_made) * 100, 1)
            
            print(f"{status:20} {api_name:15} | Calls: {stats.calls_made:3} | Success: {success_rate:5.1f}% | Failures: {stats.consecutive_failures}")
            
            if stats.last_error:
                print(f"                     {'':15} | Last Error: {stats.last_error[:50]}...")
        
        print("=" * 55)
        print("🎯 Strategy: React to rate limits, switch APIs dynamically")
        print("🔄 Google APIs prioritized, fallbacks available")
        print("=" * 55)
    
    def get_best_api(self, chunk_analysis: Dict) -> Optional[str]:
        """
        Get the best available API based on chunk analysis - reactive approach
        """
        # Get currently available APIs (those not in cooldown)
        available_apis = self._get_available_apis()
        
        if not available_apis:
            return None
        
        # Priority routing based on chunk analysis
        has_indic_script = chunk_analysis.get("has_indic_script", False)
        priority = chunk_analysis.get("priority", "medium")
        complexity = chunk_analysis.get("complexity", "medium")
        
        # Critical priority: Must use Google for Indic scripts
        if has_indic_script:
            google_apis = [api for api in available_apis if api.startswith('google')]
            if google_apis:
                return self._choose_least_used_api(google_apis)
            else:
                print("⚠️ Warning: No Google APIs available for Indic content")
                return available_apis[0] if available_apis else None
        
        # High priority: Prefer Google APIs for complex content
        if priority == "high" or complexity == "complex":
            google_apis = [api for api in available_apis if api.startswith('google')]
            if google_apis:
                return self._choose_least_used_api(google_apis)
            # Fallback to powerful non-Google APIs
            powerful_apis = [api for api in available_apis if api in ['together_ai', 'groq']]
            if powerful_apis:
                return self._choose_least_used_api(powerful_apis)
        
        # Medium priority: Smart balancing between Google APIs first
        if priority == "medium":
            google_apis = [api for api in available_apis if api.startswith('google')]
            if google_apis and len(google_apis) > 1:
                return self._smart_balance_google_apis(google_apis)
            elif google_apis:
                return google_apis[0]
            # Fallback to other APIs
            return self._choose_least_used_api(available_apis)
        
        # Low priority: Use any available API, but prefer Google first
        return self._choose_least_used_api(available_apis)
    
    def _get_available_apis(self) -> List[str]:
        """Get list of currently available APIs (not in cooldown)"""
        available = []
        
        for api_name, config in self.api_configs.items():
            # Check if API key exists
            if not config['key']:
                continue
            
            # Check if API is currently available (not in cooldown)
            if self._is_api_currently_available(api_name):
                available.append(api_name)
        
        # Sort by priority (lower number = higher priority)
        available.sort(key=lambda x: self.api_configs[x]['priority'])
        return available
    
    def _choose_least_used_api(self, api_list: List[str]) -> Optional[str]:
        """Choose the API with least recent failures from the given list"""
        if not api_list:
            return None
        
        if len(api_list) == 1:
            return api_list[0]
        
        # Sort by consecutive failures (ascending) and last call time
        api_scores = []
        for api_name in api_list:
            stats = self.usage_stats[api_name]
            # Score based on consecutive failures and recency
            score = stats.consecutive_failures * 1000 + (time.time() - stats.last_call_time) / 3600
            api_scores.append((api_name, score))
        
        # Sort by score (ascending - lower is better)
        api_scores.sort(key=lambda x: x[1])
        return api_scores[0][0]
    
    def _smart_balance_google_apis(self, google_apis: List[str]) -> str:
        """Smart load balancing between Google APIs"""
        if len(google_apis) == 1:
            return google_apis[0]
        
        # Balance based on consecutive failures and recent usage
        primary_stats = self.usage_stats.get('google_primary', self.usage_stats[google_apis[0]])
        secondary_stats = self.usage_stats.get('google_secondary', self.usage_stats[google_apis[1]] if len(google_apis) > 1 else primary_stats)
        
        # Choose the one with fewer consecutive failures, then by last use time
        if primary_stats.consecutive_failures < secondary_stats.consecutive_failures:
            return 'google_primary' if 'google_primary' in google_apis else google_apis[0]
        elif secondary_stats.consecutive_failures < primary_stats.consecutive_failures:
            return 'google_secondary' if 'google_secondary' in google_apis else google_apis[1] if len(google_apis) > 1 else google_apis[0]
        else:
            # Equal failures, choose by last use time
            if primary_stats.last_call_time < secondary_stats.last_call_time:
                return 'google_primary' if 'google_primary' in google_apis else google_apis[0]
            else:
                return 'google_secondary' if 'google_secondary' in google_apis else google_apis[1] if len(google_apis) > 1 else google_apis[0]
    
    def get_available_apis(self) -> List[str]:
        """Public method to get available APIs (for routing engine)"""
        return self._get_available_apis()
