import time
import asyncio
from typing import Dict, Any, Optional
import google.generativeai as genai
import requests
from openai import OpenAI
import together

from .chunk_complexity_analyzer import ChunkComplexityAnalyzer
from .smart_api_manager import SmartAPIManager

class LLMRoutingEngine:
    """
    Core routing engine that intelligently routes requests to the best available API
    """
    
    def __init__(self):
        self.complexity_analyzer = ChunkComplexityAnalyzer()
        self.api_manager = SmartAPIManager()
        
        # Initialize API clients
        self._setup_api_clients()
        
        print("🚀 LLM Routing Engine initialized successfully")
    
    def _setup_api_clients(self):
        """Initialize all API clients"""
        # Google Generative AI (both keys use same client, different keys)
        primary_key = self.api_manager.get_api_config('google_primary')['key']
        if primary_key:
            genai.configure(api_key=primary_key)
        
        # GROQ client
        groq_key = self.api_manager.get_api_config('groq')['key']
        self.groq_client = OpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1"
        ) if groq_key else None
        
        # Together AI client
        together_key = self.api_manager.get_api_config('together_ai')['key']
        if together_key:
            together.api_key = together_key
        
        # OpenRouter client
        openrouter_key = self.api_manager.get_api_config('openrouter')['key']
        self.openrouter_client = OpenAI(
            api_key=openrouter_key,
            base_url="https://openrouter.ai/api/v1"
        ) if openrouter_key else None
    
    async def route_and_execute(self, 
                               text_chunk: str, 
                               task_type: str = "summarize",
                               system_prompt: str = None,
                               user_prompt: str = None,
                               emergency_mode: bool = False,
                               max_retries: int = 3) -> Dict[str, Any]:
        """
        Main routing and execution method with intelligent fallback
        """
        # Step 1: Analyze chunk complexity
        chunk_analysis = self.complexity_analyzer.analyze_chunk(text_chunk)
        
        # Step 2: Try multiple APIs with intelligent fallback
        attempt_count = 0
        tried_apis = set()
        
        while attempt_count < max_retries:
            # Get next best API (excluding already tried ones)
            available_apis = self.api_manager.get_available_apis()
            remaining_apis = [api for api in available_apis if api not in tried_apis]
            
            if not remaining_apis:
                # If no APIs available and we haven't tried emergency reset
                if not emergency_mode:
                    print("🚨 No APIs available, forcing cooldown reset...")
                    self.api_manager.force_enable_all_apis()
                    emergency_mode = True
                    available_apis = self.api_manager.get_available_apis()
                    remaining_apis = [api for api in available_apis if api not in tried_apis]
                
                if not remaining_apis:
                    return {
                        "success": False,
                        "error": f"All APIs exhausted after {attempt_count} attempts. Tried: {list(tried_apis)}",
                        "analysis": chunk_analysis,
                        "tried_apis": list(tried_apis)
                    }
            
            # Select best API from remaining options
            selected_api = self._select_best_from_remaining(remaining_apis, chunk_analysis)
            tried_apis.add(selected_api)
            
            print(f"🔄 Attempt {attempt_count + 1}: Trying {selected_api}")
            
            # Step 3: Execute with selected API
            result = await self._execute_with_api(
                api_name=selected_api,
                text_chunk=text_chunk,
                task_type=task_type,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                chunk_analysis=chunk_analysis
            )
            
            # Step 4: Record result
            error_message = result.get("error", "")
            is_success = result.get("success", False)
            
            self.api_manager.record_api_call(
                api_name=selected_api,
                success=is_success,
                error_message=error_message
            )
            
            # Step 5: Check if we should retry
            if is_success:
                print(f"✅ Success with {selected_api}")
                result["attempts_made"] = attempt_count + 1
                result["tried_apis"] = list(tried_apis)
                return result
            
            # Check if error is retryable
            should_retry = self._should_retry_error(error_message, selected_api)
            
            if should_retry:
                print(f"⚠️ {selected_api} failed with retryable error: {error_message[:100]}...")
                attempt_count += 1
                
                # Add delay before retry
                if attempt_count < max_retries:
                    await asyncio.sleep(2)
                continue
            else:
                print(f"❌ {selected_api} failed with non-retryable error: {error_message[:100]}...")
                # Don't increment attempt_count for non-retryable errors, just try next API
                continue
        
        # All attempts failed
        return {
            "success": False,
            "error": f"All APIs failed after {attempt_count} attempts",
            "analysis": chunk_analysis,
            "tried_apis": list(tried_apis),
            "attempts_made": attempt_count
        }
    
    def _select_best_from_remaining(self, remaining_apis: list, chunk_analysis: Dict) -> str:
        """Select best API from remaining options"""
        if not remaining_apis:
            return None
            
        # Priority logic - prefer Google for Indic scripts
        has_indic_script = chunk_analysis.get("has_indic_script", False)
        priority = chunk_analysis.get("priority", "medium")
        
        # Critical: Must use Google for Indic scripts
        if has_indic_script:
            google_apis = [api for api in remaining_apis if api.startswith('google')]
            if google_apis:
                return self.api_manager._choose_least_used_api(google_apis)
        
        # High priority: Prefer Google APIs
        if priority == "high" or chunk_analysis.get("complexity") == "complex":
            google_apis = [api for api in remaining_apis if api.startswith('google')]
            if google_apis:
                return self.api_manager._choose_least_used_api(google_apis)
            # Fallback to powerful non-Google APIs
            powerful_apis = [api for api in remaining_apis if api in ['together_ai', 'groq']]
            if powerful_apis:
                return self.api_manager._choose_least_used_api(powerful_apis)
        
        # Return least used from remaining
        return self.api_manager._choose_least_used_api(remaining_apis)
    
    def _should_retry_error(self, error_message: str, api_name: str) -> bool:
        """Determine if an error is retryable"""
        if not error_message:
            return False
            
        error_lower = error_message.lower()
        
        # These errors should try a different API, not retry same API
        if any(keyword in error_lower for keyword in [
            "quota", "exceeded", "429", "rate limit", 
            "billing", "quota_exceeded", "insufficient_quota"
        ]):
            print(f"🔄 {api_name} quota/rate limit hit, switching to different API")
            return False  # Don't retry same API, try different one
            
        # These are retryable with same API
        if any(keyword in error_lower for keyword in [
            "timeout", "connection", "network", "502", "503", "504"
        ]):
            return True
            
        # Unknown errors - try different API
        return False
    
    async def _execute_with_api(self, 
                               api_name: str, 
                               text_chunk: str,
                               task_type: str,
                               system_prompt: str,
                               user_prompt: str,
                               chunk_analysis: Dict) -> Dict[str, Any]:
        """
        Execute request with specific API
        """
        config = self.api_manager.get_api_config(api_name)
        
        # Add delay before API call
        delay = self.api_manager.get_api_delay(api_name)
        if delay > 0:
            await asyncio.sleep(delay)
        
        try:
            if api_name.startswith('google'):
                return await self._execute_google(api_name, text_chunk, task_type, system_prompt, user_prompt, chunk_analysis)
            elif api_name == 'groq':
                return await self._execute_groq(text_chunk, task_type, system_prompt, user_prompt, chunk_analysis)
            elif api_name == 'together_ai':
                return await self._execute_together_ai(text_chunk, task_type, system_prompt, user_prompt, chunk_analysis)
            elif api_name == 'openrouter':
                return await self._execute_openrouter(text_chunk, task_type, system_prompt, user_prompt, chunk_analysis)
            else:
                return {"success": False, "error": f"Unknown API: {api_name}"}
        
        except Exception as e:
            print(f"❌ Error executing with {api_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "api_used": api_name,
                "analysis": chunk_analysis
            }
    
    async def _execute_google(self, api_name: str, text_chunk: str, task_type: str, 
                            system_prompt: str, user_prompt: str, chunk_analysis: Dict) -> Dict[str, Any]:
        """Execute with Google Generative AI"""
        try:
            # Set the correct API key for this specific call
            config = self.api_manager.get_api_config(api_name)
            genai.configure(api_key=config['key'])
            
            model = genai.GenerativeModel(config['model'])
            
            # Build prompt
            full_prompt = self._build_prompt(text_chunk, task_type, system_prompt, user_prompt, chunk_analysis)
            
            # Execute with retry logic
            response = await asyncio.to_thread(model.generate_content, full_prompt)
            
            if response and response.text:
                return {
                    "success": True,
                    "content": response.text.strip(),
                    "api_used": api_name,
                    "model": config['model'],
                    "analysis": chunk_analysis
                }
            else:
                return {
                    "success": False,
                    "error": "Empty response from Google API",
                    "api_used": api_name
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Google API error: {str(e)}",
                "api_used": api_name,
                "analysis": chunk_analysis
            }
    
    async def _execute_groq(self, text_chunk: str, task_type: str, 
                           system_prompt: str, user_prompt: str, chunk_analysis: Dict) -> Dict[str, Any]:
        """Execute with GROQ API"""
        if not self.groq_client:
            return {"success": False, "error": "GROQ client not initialized"}
        
        try:
            config = self.api_manager.get_api_config('groq')
            
            # Build messages
            messages = self._build_chat_messages(text_chunk, task_type, system_prompt, user_prompt, chunk_analysis)
            
            # Execute
            response = await asyncio.to_thread(
                self.groq_client.chat.completions.create,
                model=config['model'],
                messages=messages,
                max_tokens=2000,
                temperature=0.1
            )
            
            if response and response.choices:
                return {
                    "success": True,
                    "content": response.choices[0].message.content.strip(),
                    "api_used": "groq",
                    "model": config['model'],
                    "analysis": chunk_analysis
                }
            else:
                return {
                    "success": False,
                    "error": "Empty response from GROQ",
                    "api_used": "groq"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"GROQ API error: {str(e)}",
                "api_used": "groq",
                "analysis": chunk_analysis
            }
    
    async def _execute_together_ai(self, text_chunk: str, task_type: str,
                                  system_prompt: str, user_prompt: str, chunk_analysis: Dict) -> Dict[str, Any]:
        """Execute with Together AI"""
        try:
            config = self.api_manager.get_api_config('together_ai')
            
            # Build prompt
            full_prompt = self._build_prompt(text_chunk, task_type, system_prompt, user_prompt, chunk_analysis)
            
            # Execute
            response = await asyncio.to_thread(
                together.Complete.create,
                prompt=full_prompt,
                model=config['model'],
                max_tokens=2000,
                temperature=0.1
            )
            
            if response and response.get('output', {}).get('choices'):
                return {
                    "success": True,
                    "content": response['output']['choices'][0]['text'].strip(),
                    "api_used": "together_ai",
                    "model": config['model'],
                    "analysis": chunk_analysis
                }
            else:
                return {
                    "success": False,
                    "error": "Empty response from Together AI",
                    "api_used": "together_ai"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Together AI error: {str(e)}",
                "api_used": "together_ai",
                "analysis": chunk_analysis
            }
    
    async def _execute_openrouter(self, text_chunk: str, task_type: str,
                                 system_prompt: str, user_prompt: str, chunk_analysis: Dict) -> Dict[str, Any]:
        """Execute with OpenRouter"""
        if not self.openrouter_client:
            return {"success": False, "error": "OpenRouter client not initialized"}
        
        try:
            config = self.api_manager.get_api_config('openrouter')
            
            # Build messages
            messages = self._build_chat_messages(text_chunk, task_type, system_prompt, user_prompt, chunk_analysis)
            
            # Execute
            response = await asyncio.to_thread(
                self.openrouter_client.chat.completions.create,
                model=config['model'],
                messages=messages,
                max_tokens=2000,
                temperature=0.1
            )
            
            if response and response.choices:
                return {
                    "success": True,
                    "content": response.choices[0].message.content.strip(),
                    "api_used": "openrouter",
                    "model": config['model'],
                    "analysis": chunk_analysis
                }
            else:
                return {
                    "success": False,
                    "error": "Empty response from OpenRouter",
                    "api_used": "openrouter"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"OpenRouter error: {str(e)}",
                "api_used": "openrouter",
                "analysis": chunk_analysis
            }
    
    def _build_prompt(self, text_chunk: str, task_type: str, system_prompt: str, 
                     user_prompt: str, chunk_analysis: Dict) -> str:
        """Build prompt for single-prompt APIs (Google, Together AI)"""
        # Use provided prompts or build default
        if system_prompt and user_prompt:
            return f"{system_prompt}\n\n{user_prompt}\n\nText to process:\n{text_chunk}"
        
        # Default summarization prompt
        if task_type == "summarize":
            language_hint = ""
            if chunk_analysis.get("has_indic_script"):
                language_hint = "\nIMPORTANT: This text contains Hindi/Urdu/Bengali content. Preserve and understand the Indic script content properly."
            
            return f"""You are a highly skilled summarization expert. Create a concise, informative summary of the following text.{language_hint}

Text to summarize:
{text_chunk}

Provide a clear, well-structured summary that captures the main points and key information."""
        
        return f"Process this text for {task_type}:\n\n{text_chunk}"
    
    def _build_chat_messages(self, text_chunk: str, task_type: str, system_prompt: str,
                            user_prompt: str, chunk_analysis: Dict) -> list:
        """Build messages for chat-based APIs (GROQ, OpenRouter)"""
        messages = []
        
        # System message
        if system_prompt:
            system_message = system_prompt
        else:
            system_message = "You are a highly skilled AI assistant specializing in text processing and summarization."
            if chunk_analysis.get("has_indic_script"):
                system_message += " You have expertise in handling Hindi, Urdu, Bengali and other Indic scripts."
        
        messages.append({"role": "system", "content": system_message})
        
        # User message
        if user_prompt:
            full_user_message = f"{user_prompt}\n\nText to process:\n{text_chunk}"
        else:
            if task_type == "summarize":
                full_user_message = f"Please create a concise, informative summary of the following text:\n\n{text_chunk}"
            else:
                full_user_message = f"Please process this text for {task_type}:\n\n{text_chunk}"
        
        messages.append({"role": "user", "content": full_user_message})
        
        return messages
    
    def get_routing_stats(self) -> Dict:
        """Get comprehensive routing statistics"""
        return {
            "api_manager_stats": self.api_manager.get_usage_summary(),
            "routing_engine_info": {
                "total_apis_configured": len(self.api_manager.api_configs),
                "available_apis": len(self.api_manager._get_available_apis()),
                "emergency_mode_apis": len(self.api_manager._get_available_apis(emergency_mode=True))
            }
        }
    
    def print_status(self):
        """Print comprehensive status"""
        print("\n🎯 LLM Routing Engine Status")
        self.api_manager.print_status()
        stats = self.get_routing_stats()
        routing_info = stats["routing_engine_info"]
        print(f"\n📊 Routing Summary:")
        print(f"Available APIs: {routing_info['available_apis']}/{routing_info['total_apis_configured']}")
        print(f"Emergency APIs: {routing_info['emergency_mode_apis']}")
