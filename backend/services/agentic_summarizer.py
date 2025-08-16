import time
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from services.llm import get_gemma_llm

class AgenticSummarizer:
    def __init__(self):
        self.chunk_size = 4000  # Larger chunks = fewer API calls
        self.max_workers = 1    # Sequential processing for free tier
        self.llm = get_gemma_llm()
        self.delay_between_calls = 2  # Seconds between API calls
    
    def fast_summarize(self, pdf_content: str, filename: str) -> Dict:
        """Main orchestrator for agentic summarization"""
        try:
            print(f"Starting agentic summarization for {filename}")
            start_time = time.time()
            
            # Step 1: Divide content into chunks
            chunks = self.divide_content(pdf_content)
            print(f"Divided into {len(chunks)} chunks")
            
            # Step 2: Create specialized agent tasks
            tasks = self.create_agent_tasks(chunks)
            
            # Step 3: Process chunks sequentially to avoid rate limits
            partial_summaries = self.process_sequential_smart(tasks)
            
            # Step 4: Synthesize final summary
            final_summary = self.synthesize_summaries(partial_summaries)
            
            end_time = time.time()
            processing_time = round(end_time - start_time, 2)
            
            print(f"Agentic summarization completed in {processing_time} seconds")
            
            return {
                "filename": filename,
                "summary": final_summary,
                "processing_time": processing_time,
                "chunks_processed": len(chunks),
                "method": "agentic"
            }
            
        except Exception as e:
            print(f"Error in agentic summarization: {str(e)}")
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
    
    def create_agent_tasks(self, chunks: List[str]) -> List[Dict]:
        """Create specialized tasks for different agents"""
        tasks = []
        
        for i, chunk in enumerate(chunks):
            # Assign different roles based on chunk position
            if i == 0:
                agent_type = "introduction_agent"
                prompt = """You are an expert at identifying main topics and introductions. 
                Summarize the main topic, purpose, and key themes introduced in this text. 
                Focus on what this document is about and its primary objectives."""
                
            elif i == len(chunks) - 1:
                agent_type = "conclusion_agent"
                prompt = """You are an expert at extracting conclusions and key outcomes. 
                Summarize the conclusions, results, findings, and final takeaways from this text. 
                Focus on what was achieved or concluded."""
                
            else:
                agent_type = "content_agent"
                prompt = """You are an expert at extracting key information and main points. 
                Summarize the important details, methodologies, concepts, and significant information in this text. 
                Focus on the core content and valuable insights."""
            
            tasks.append({
                "agent_type": agent_type,
                "chunk_id": i,
                "content": chunk,
                "prompt": prompt
            })
        
        return tasks
    
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
