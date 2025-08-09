import time
import asyncio
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from services.llm import get_gemini_flash_llm
from services.chunk_complexity_analyzer import ChunkComplexityAnalyzer
from services.smart_api_manager import SmartAPIManager
from services.llm_routing_engine import LLMRoutingEngine

class AgenticSummarizer:
    """
    Advanced Agentic Summarizer with LLM Router Integration
    
    This summarizer uses specialized AI agents to process different parts of documents:
    - Introduction Agent: Analyzes opening sections, identifies thesis and context
    - Content Agent: Processes main content, extracts key points and details  
    - Conclusion Agent: Handles endings, captures outcomes and implications
    - Synthesis: Combines all agent outputs into coherent final summary
    
    Features:
    - Intelligent LLM routing across 5 APIs (Gemma, GROQ, Together AI, OpenRouter)
    - Reactive rate limit handling with automatic fallbacks
    - Complexity-aware agent assignment
    - Semantic chunking with paragraph boundary respect
    - Production-ready error handling and recovery
    """
    def __init__(self):
        self.chunk_size = 4000  # Larger chunks = fewer API calls
        self.max_workers = 1    # Sequential processing for free tier
        self.delay_between_calls = 2  # Seconds between API calls
        
        # Enhanced LLM Router components
        try:
            self.complexity_analyzer = ChunkComplexityAnalyzer()
            self.api_manager = SmartAPIManager()
            self.routing_engine = LLMRoutingEngine()
            self.use_router = True
            print("🚀 Enhanced AgenticSummarizer with LLM Router initialized")
        except Exception as e:
            print(f"⚠️ LLM Router initialization failed, falling back to single LLM: {e}")
            self.llm = get_gemini_flash_llm()
            self.use_router = False
    
    def fast_summarize(self, pdf_content: str, filename: str) -> Dict:
        """Main orchestrator for enhanced agentic summarization with LLM Router"""
        try:
            print(f"🚀 Starting enhanced agentic summarization for {filename}")
            start_time = time.time()
            
            # Step 1: Divide content into chunks
            chunks = self.divide_content(pdf_content)
            print(f"📄 Divided into {len(chunks)} chunks")
            
            # Step 2: Create specialized agent tasks with complexity analysis
            tasks = self.create_enhanced_agent_tasks(chunks)
            
            # Step 3: Process chunks with smart routing
            if self.use_router:
                partial_summaries = self.process_with_router(tasks)
            else:
                partial_summaries = self.process_sequential_smart(tasks)
            
            # Step 4: Synthesize final summary
            if self.use_router:
                final_summary = self.synthesize_with_router(partial_summaries, filename)
            else:
                final_summary = self.synthesize_summaries(partial_summaries)
            
            end_time = time.time()
            processing_time = round(end_time - start_time, 2)
            
            print(f"✅ Enhanced agentic summarization completed in {processing_time} seconds")
            
            result = {
                "filename": filename,
                "summary": final_summary,
                "processing_time": processing_time,
                "chunks_processed": len(chunks),
                "method": "enhanced_agentic"
            }
            
            # Add router stats if available
            if self.use_router:
                result["router_stats"] = self.api_manager.get_usage_summary()
                result["routing_engine_used"] = True
            
            return result
            
        except Exception as e:
            print(f"❌ Error in enhanced agentic summarization: {str(e)}")
            raise e
    
    def divide_content(self, content: str) -> List[str]:
        """Smart content division respecting paragraph boundaries"""
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # Check if adding this paragraph exceeds chunk size
            if len(current_chunk + paragraph) < self.chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                # Save current chunk if it has content
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                # Start new chunk with current paragraph
                current_chunk = paragraph + "\n\n"
        
        # Add final chunk if it has content
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Ensure we have at least one chunk
        if not chunks and content.strip():
            chunks.append(content.strip())
            
        return chunks
    
    def create_enhanced_agent_tasks(self, chunks: List[str]) -> List[Dict]:
        """Create specialized tasks with complexity analysis for enhanced routing"""
        tasks = []
        
        for i, chunk in enumerate(chunks):
            # Analyze chunk complexity and language
            if self.use_router:
                analysis = self.complexity_analyzer.analyze_chunk(chunk)
            else:
                analysis = {"complexity": "medium", "language": "en", "priority": "medium"}
            
            # Assign different roles based on chunk position with enhanced prompts
            if i == 0:
                agent_type = "introduction_agent"
                prompt = """You are an Introduction Analysis Specialist. Your role is to analyze the beginning portion of documents and create compelling introductory summaries. You excel at identifying the main thesis, purpose, and setting the context for the entire document.

                Analyze this introductory section and create a concise summary that:
                1. Captures the main purpose and thesis
                2. Identifies key context and background
                3. Sets up the reader for what follows
                4. Maintains the original tone and intent

                Create a well-structured introduction summary:"""
                
            elif i == len(chunks) - 1:
                agent_type = "conclusion_agent"
                prompt = """You are a Conclusion Analysis Specialist. Your role is to analyze concluding sections and synthesize final summaries that capture outcomes, results, and final thoughts. You excel at identifying implications and wrap-up elements.

                Analyze this concluding section and create a final summary that:
                1. Captures main conclusions and outcomes
                2. Identifies key findings and results
                3. Notes implications and future directions
                4. Provides proper closure to the content

                Create a comprehensive conclusion summary:"""
                
            else:
                agent_type = "content_agent"
                prompt = """You are a Content Analysis Specialist. Your role is to analyze main content sections and extract the core information, key points, and essential details. You excel at distilling complex content into clear, informative summaries.

                Analyze this content section and create a comprehensive summary that:
                1. Extracts all key points and main ideas
                2. Preserves important details and data
                3. Maintains logical flow and structure
                4. Keeps technical accuracy intact

                Create a detailed content summary:"""
            
            tasks.append({
                "agent_type": agent_type,
                "chunk_id": i,
                "content": chunk,
                "prompt": prompt,
                "complexity": analysis.get("complexity", "medium"),
                "language": analysis.get("language", "en"),
                "priority": analysis.get("priority", "medium"),
                "has_indic_script": analysis.get("has_indic_script", False)
            })
        
        return tasks
    
    def process_with_router(self, tasks: List[Dict]) -> List[str]:
        """Process tasks using LLM Router with async support"""
        try:
            # Run async processing in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                results = loop.run_until_complete(self._async_process_tasks(tasks))
            finally:
                loop.close()
                
            return results
            
        except Exception as e:
            print(f"❌ Router processing failed: {e}")
            # Fallback to original processing
            return self.process_sequential_smart(tasks)
    
    async def _async_process_tasks(self, tasks: List[Dict]) -> List[str]:
        """Async processing of tasks with LLM Router and intelligent fallback"""
        results = []
        
        for i, task in enumerate(tasks):
            print(f"🤖 Processing chunk {i+1}/{len(tasks)} with {task['agent_type']} (complexity: {task['complexity']})")
            
            success = False
            attempts = 0
            max_attempts = 2
            
            while not success and attempts < max_attempts:
                try:
                    # Build full prompt
                    full_prompt = f"{task['prompt']}\n\nText to summarize:\n{task['content']}"
                    
                    # Route to best API with emergency mode on second attempt
                    emergency_mode = attempts > 0
                    
                    result = await self.routing_engine.route_and_execute(
                        text_chunk=task['content'],
                        task_type="summarize",
                        system_prompt="You are an expert document summarization assistant with specialized agent capabilities.",
                        user_prompt=full_prompt,
                        emergency_mode=emergency_mode
                    )
                    
                    if result["success"]:
                        summary = result["content"]
                        results.append(summary)
                        tried_apis = result.get("tried_apis", [])
                        attempts_made = result.get("attempts_made", 1)
                        print(f"    ✅ Completed with {result.get('api_used', 'unknown')} (tried: {tried_apis}, attempts: {attempts_made})")
                        success = True
                    else:
                        attempts += 1
                        error_msg = result.get('error', 'Unknown error')
                        tried_apis = result.get("tried_apis", [])
                        
                        if attempts < max_attempts:
                            print(f"    ⚠️ Attempt {attempts} failed, retrying with emergency mode...")
                            print(f"        Error: {error_msg}")
                            print(f"        Tried APIs: {tried_apis}")
                            await asyncio.sleep(3)  # Wait before retry
                        else:
                            print(f"    ❌ All attempts failed for chunk {i+1}")
                            print(f"        Final error: {error_msg}")
                            print(f"        Tried APIs: {tried_apis}")
                            
                            # Fallback to original LLM if router completely fails
                            try:
                                print(f"    🔄 Attempting fallback to original LLM...")
                                fallback_result = await asyncio.to_thread(
                                    self._fallback_to_original_llm, 
                                    task
                                )
                                results.append(fallback_result)
                                print(f"    ✅ Fallback successful")
                                success = True
                            except Exception as fallback_error:
                                print(f"    ❌ Fallback also failed: {fallback_error}")
                                results.append(f"Error processing section {i+1}: All methods failed")
                                success = True  # Stop trying
                
                except Exception as e:
                    attempts += 1
                    print(f"    ❌ Exception in attempt {attempts} for chunk {i+1}: {e}")
                    if attempts >= max_attempts:
                        results.append(f"Error processing section {i+1}: {str(e)}")
                        success = True  # Stop trying
            
            # Maintain delay between chunks only if successful
            if i < len(tasks) - 1:
                await asyncio.sleep(self.delay_between_calls)
        
        return results
    
    def _fallback_to_original_llm(self, task: Dict) -> str:
        """Fallback to original LLM when router fails completely"""
        try:
            # Import here to avoid circular dependency
            from services.llm import get_gemini_flash_llm
            
            llm = get_gemini_flash_llm()
            full_prompt = f"{task['prompt']}\n\nText to summarize:\n{task['content']}"
            
            response = llm.invoke(full_prompt)
            
            if hasattr(response, 'content'):
                return response.content.strip()
            else:
                return str(response).strip()
                
        except Exception as e:
            return f"Fallback processing failed for section {task['chunk_id'] + 1}: {str(e)}"
    
    def synthesize_with_router(self, partial_summaries: List[str], filename: str) -> str:
        """Synthesize final summary using LLM Router"""
        try:
            print("🔄 Synthesizing final summary with router...")
            
            if not partial_summaries:
                return "No summaries available for synthesis."
            
            if len(partial_summaries) == 1:
                return partial_summaries[0]
            
            # Combine all partial summaries
            combined_content = ""
            for i, summary in enumerate(partial_summaries):
                if "Error" not in summary:  # Skip error summaries
                    combined_content += f"Section {i+1} Summary:\n{summary}\n\n"
            
            # Create enhanced synthesis prompt
            synthesis_prompt = f"""You are a Document Synthesis Specialist. Your role is to combine multiple section summaries into one coherent, comprehensive document summary. You excel at creating unified narratives from diverse content pieces.

            You have been given multiple section summaries from the document "{filename}". 
            Your task is to synthesize them into a single, comprehensive document summary.

            Create a unified summary that:
            1. Flows logically from introduction to conclusion
            2. Maintains all key information from each section
            3. Eliminates redundancy while preserving completeness
            4. Creates a coherent narrative structure
            5. Preserves the document's original intent and tone

            Section summaries to synthesize:
            
            {combined_content}
            
            Final comprehensive summary:"""
            
            # Use router for synthesis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.routing_engine.route_and_execute(
                        text_chunk="",  # Empty chunk for synthesis
                        task_type="synthesis",
                        system_prompt="You are an expert document synthesis specialist.",
                        user_prompt=synthesis_prompt
                    )
                )
            finally:
                loop.close()
            
            if result["success"]:
                print("✅ Synthesis completed successfully")
                return result["content"].strip()
            else:
                print(f"⚠️ Synthesis failed: {result.get('error', 'Unknown error')}")
                # Fallback to simple concatenation
                return "\n\n".join([f"Section {i+1}: {summary}" 
                                   for i, summary in enumerate(partial_summaries)])
            
        except Exception as e:
            print(f"❌ Error in router synthesis: {str(e)}")
            # Fallback to original synthesis
            return self.synthesize_summaries(partial_summaries)
    
    def process_sequential_smart(self, tasks: List[Dict]) -> List[str]:
        """Process tasks sequentially with smart rate limiting for free tier"""
        results = []
        
        for i, task in enumerate(tasks):
            print(f"Processing chunk {i+1}/{len(tasks)} with {task['agent_type']}")
            
            try:
                result = self.call_llm_agent_with_retry(task)
                results.append(result)
                
                # Smart delay only between requests (not after last one)
                if i < len(tasks) - 1:
                    print(f"Waiting {self.delay_between_calls} seconds before next chunk...")
                    time.sleep(self.delay_between_calls)
                    
            except Exception as e:
                print(f"Failed to process chunk {i+1}: {str(e)}")
                results.append(f"Error in chunk {i+1}: {str(e)}")
        
        return results
    
    def call_llm_agent_with_retry(self, task: Dict, max_retries=3) -> str:
        """Call LLM with intelligent retry logic for rate limits"""
        for attempt in range(max_retries):
            try:
                return self.call_llm_agent(task)
                
            except Exception as e:
                error_str = str(e)
                
                if "429" in error_str:  # Rate limit error
                    if attempt < max_retries - 1:
                        # Extract wait time from error or use default
                        wait_time = 35 if "retry_delay" in error_str else 30
                        print(f"Rate limited (attempt {attempt+1}), waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return f"Rate limit exceeded after {max_retries} attempts"
                        
                elif "quota" in error_str.lower():  # Quota exceeded
                    print(f"Quota exceeded, using fallback summary for chunk {task['chunk_id']}")
                    return f"Summary for section {task['chunk_id'] + 1} unavailable due to quota limits"
                
                else:
                    # Other errors, retry with shorter delay
                    if attempt < max_retries - 1:
                        print(f"Error (attempt {attempt+1}): {error_str[:100]}... Retrying in 5 seconds...")
                        time.sleep(5)
                        continue
                    else:
                        return f"Error processing section {task['chunk_id'] + 1}: {error_str[:200]}"
        
        return f"Failed to process chunk {task['chunk_id']} after {max_retries} attempts"
    
    def call_llm_agent(self, task: Dict) -> str:
        """Call Gemma 3 with specific agent role"""
        try:
            print(f"Processing chunk {task['chunk_id'] + 1} with {task['agent_type']}")
            
            # Create the full prompt with role and content
            full_prompt = f"{task['prompt']}\n\nText to summarize:\n{task['content']}"
            
            # Call Gemma 3 via LangChain
            response = self.llm.invoke(full_prompt)
            
            # Extract content from response
            if hasattr(response, 'content'):
                summary = response.content
            else:
                summary = str(response)
            
            print(f"Completed chunk {task['chunk_id'] + 1}")
            return summary.strip()
            
        except Exception as e:
            print(f"Error processing chunk {task['chunk_id']}: {str(e)}")
            return f"Error processing section {task['chunk_id'] + 1}: {str(e)}"
    
    def synthesize_summaries(self, partial_summaries: List[str]) -> str:
        """Combine all partial summaries into final coherent summary"""
        try:
            print("Synthesizing final summary...")
            
            # Combine all partial summaries
            combined_content = ""
            for i, summary in enumerate(partial_summaries):
                combined_content += f"Section {i+1} Summary:\n{summary}\n\n"
            
            # Create synthesis prompt
            synthesis_prompt = f"""You are an expert at creating coherent, well-structured summaries. 
            You have been given multiple section summaries from a document. 
            Your task is to combine them into one unified, comprehensive summary that flows naturally.
            
            Instructions:
            - Create a single, coherent summary that covers all important points
            - Maintain logical flow and structure
            - Remove redundancy while preserving key information
            - Make it readable and well-organized
            - Keep the essential details from each section
            
            Section summaries to combine:
            
            {combined_content}
            
            Please provide a unified summary:"""
            
            # Call Gemma 3 for final synthesis
            response = self.llm.invoke(synthesis_prompt)
            
            # Extract final summary
            if hasattr(response, 'content'):
                final_summary = response.content
            else:
                final_summary = str(response)
            
            print("Final synthesis completed")
            return final_summary.strip()
            
        except Exception as e:
            print(f"Error in synthesis: {str(e)}")
            # Fallback: return combined summaries if synthesis fails
            return "\n\n".join([f"Section {i+1}: {summary}" 
                               for i, summary in enumerate(partial_summaries)])
