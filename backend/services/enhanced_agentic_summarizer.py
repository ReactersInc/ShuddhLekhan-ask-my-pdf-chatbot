import asyncio
import time
from typing import List, Dict, Any, Optional
from .llm_routing_engine import LLMRoutingEngine

class EnhancedAgenticSummarizer:
    """
    Enhanced Agentic Summarizer that uses LLM Router for intelligent API selection
    """
    
    def __init__(self):
        self.llm_router = LLMRoutingEngine()
        
        # Agent configurations with specialized prompts
        self.agents = {
            "introduction_agent": {
                "system_prompt": """You are an Introduction Analysis Specialist. Your role is to analyze the beginning portion of documents and create compelling introductory summaries. You excel at identifying the main thesis, purpose, and setting the context for the entire document.""",
                "user_prompt": """Analyze this introductory section and create a concise summary that:
1. Captures the main purpose and thesis
2. Identifies key context and background
3. Sets up the reader for what follows
4. Maintains the original tone and intent

Create a well-structured introduction summary:""",
                "priority": "high"  # Introduction often sets language/complexity tone
            },
            
            "content_agent": {
                "system_prompt": """You are a Content Analysis Specialist. Your role is to analyze main content sections and extract the core information, key points, and essential details. You excel at distilling complex content into clear, informative summaries.""",
                "user_prompt": """Analyze this content section and create a comprehensive summary that:
1. Extracts all key points and main ideas
2. Preserves important details and data
3. Maintains logical flow and structure
4. Keeps technical accuracy intact

Create a detailed content summary:""",
                "priority": "medium"
            },
            
            "conclusion_agent": {
                "system_prompt": """You are a Conclusion Analysis Specialist. Your role is to analyze concluding sections and synthesize final summaries that capture outcomes, results, and final thoughts. You excel at identifying implications and wrap-up elements.""",
                "user_prompt": """Analyze this concluding section and create a final summary that:
1. Captures main conclusions and outcomes
2. Identifies key findings and results
3. Notes implications and future directions
4. Provides proper closure to the content

Create a comprehensive conclusion summary:""",
                "priority": "high"  # Conclusions often contain critical outcomes
            },
            
            "synthesis_agent": {
                "system_prompt": """You are a Document Synthesis Specialist. Your role is to combine multiple section summaries into one coherent, comprehensive document summary. You excel at creating unified narratives from diverse content pieces.""",
                "user_prompt": """Synthesize these section summaries into a single, comprehensive document summary:

{section_summaries}

Create a unified summary that:
1. Flows logically from introduction to conclusion
2. Maintains all key information from each section
3. Eliminates redundancy while preserving completeness
4. Creates a coherent narrative structure
5. Preserves the document's original intent and tone

Final comprehensive summary:""",
                "priority": "high"  # Synthesis is critical for final quality
            }
        }
        
        print("🤖 Enhanced Agentic Summarizer with LLM Router initialized")
    
    async def summarize_document(self, chunks: List[str], 
                               chunk_type: str = "auto_detect") -> Dict[str, Any]:
        """
        Main document summarization method with intelligent routing
        """
        if not chunks:
            return {"success": False, "error": "No chunks provided"}
        
        try:
            print(f"📚 Starting agentic summarization of {len(chunks)} chunks")
            
            # Step 1: Distribute chunks to agents
            agent_assignments = self._assign_chunks_to_agents(chunks)
            
            # Step 2: Process chunks with each agent using LLM Router
            agent_results = {}
            for agent_name, assigned_chunks in agent_assignments.items():
                print(f"🔄 Processing {len(assigned_chunks)} chunks with {agent_name}")
                
                agent_results[agent_name] = await self._process_with_agent(
                    agent_name=agent_name,
                    chunks=assigned_chunks
                )
            
            # Step 3: Synthesize final summary
            final_summary = await self._synthesize_final_summary(agent_results)
            
            # Step 4: Compile comprehensive result
            result = {
                "success": True,
                "final_summary": final_summary["content"] if final_summary["success"] else "Synthesis failed",
                "agent_summaries": agent_results,
                "synthesis_details": final_summary,
                "processing_stats": self._get_processing_stats(agent_results, final_summary),
                "routing_stats": self.llm_router.get_routing_stats()
            }
            
            print("✅ Enhanced agentic summarization completed successfully")
            return result
            
        except Exception as e:
            print(f"❌ Error in enhanced agentic summarization: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "routing_stats": self.llm_router.get_routing_stats()
            }
    
    def _assign_chunks_to_agents(self, chunks: List[str]) -> Dict[str, List[str]]:
        """
        Intelligently assign chunks to specialized agents
        """
        num_chunks = len(chunks)
        
        if num_chunks == 1:
            # Single chunk - use content agent
            return {"content_agent": chunks}
        
        elif num_chunks == 2:
            # Two chunks - intro and content/conclusion
            return {
                "introduction_agent": [chunks[0]],
                "conclusion_agent": [chunks[1]]
            }
        
        elif num_chunks == 3:
            # Three chunks - perfect for intro/content/conclusion
            return {
                "introduction_agent": [chunks[0]],
                "content_agent": [chunks[1]],
                "conclusion_agent": [chunks[2]]
            }
        
        else:
            # Multiple chunks - smart distribution
            assignments = {
                "introduction_agent": [chunks[0]],  # First chunk
                "conclusion_agent": [chunks[-1]],   # Last chunk
                "content_agent": chunks[1:-1]       # Middle chunks
            }
            
            # If too many middle chunks, distribute more evenly
            middle_chunks = chunks[1:-1]
            if len(middle_chunks) > 5:  # Distribute content chunks
                mid_point = len(middle_chunks) // 2
                assignments["content_agent"] = middle_chunks[:mid_point]
                
                # Create additional content processing
                if "content_agent_2" not in assignments:
                    assignments["content_agent_2"] = middle_chunks[mid_point:]
            
            return assignments
    
    async def _process_with_agent(self, agent_name: str, chunks: List[str]) -> Dict[str, Any]:
        """
        Process chunks with specific agent using LLM Router
        """
        agent_config = self.agents.get(agent_name, self.agents["content_agent"])
        
        try:
            # Process each chunk
            chunk_summaries = []
            successful_chunks = 0
            failed_chunks = 0
            
            for i, chunk in enumerate(chunks):
                print(f"  🔄 {agent_name} processing chunk {i+1}/{len(chunks)}")
                
                # Route and execute with LLM Router
                result = await self.llm_router.route_and_execute(
                    text_chunk=chunk,
                    task_type="summarize",
                    system_prompt=agent_config["system_prompt"],
                    user_prompt=agent_config["user_prompt"]
                )
                
                if result["success"]:
                    chunk_summaries.append({
                        "chunk_index": i,
                        "summary": result["content"],
                        "api_used": result["api_used"],
                        "model": result.get("model", "unknown"),
                        "analysis": result.get("analysis", {})
                    })
                    successful_chunks += 1
                    print(f"    ✅ Chunk {i+1} completed with {result['api_used']}")
                else:
                    print(f"    ❌ Chunk {i+1} failed: {result.get('error', 'Unknown error')}")
                    failed_chunks += 1
                    
                    # Add failed chunk info
                    chunk_summaries.append({
                        "chunk_index": i,
                        "summary": f"[FAILED: {result.get('error', 'Processing failed')}]",
                        "api_used": result.get("api_used", "none"),
                        "error": result.get("error")
                    })
                
                # Add delay between chunks (as per original agentic system)
                await asyncio.sleep(2)
            
            # Combine chunk summaries into agent summary
            if successful_chunks > 0:
                combined_summary = "\n\n".join([
                    cs["summary"] for cs in chunk_summaries 
                    if not cs.get("error")
                ])
                
                return {
                    "success": True,
                    "agent_name": agent_name,
                    "summary": combined_summary,
                    "chunk_summaries": chunk_summaries,
                    "stats": {
                        "successful_chunks": successful_chunks,
                        "failed_chunks": failed_chunks,
                        "total_chunks": len(chunks)
                    }
                }
            else:
                return {
                    "success": False,
                    "agent_name": agent_name,
                    "error": "All chunks failed to process",
                    "chunk_summaries": chunk_summaries,
                    "stats": {
                        "successful_chunks": 0,
                        "failed_chunks": failed_chunks,
                        "total_chunks": len(chunks)
                    }
                }
        
        except Exception as e:
            return {
                "success": False,
                "agent_name": agent_name,
                "error": str(e),
                "stats": {
                    "successful_chunks": 0,
                    "failed_chunks": len(chunks),
                    "total_chunks": len(chunks)
                }
            }
    
    async def _synthesize_final_summary(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize final summary from all agent results
        """
        try:
            # Collect successful summaries
            section_summaries = []
            
            # Order by agent importance: intro -> content -> conclusion
            agent_order = ["introduction_agent", "content_agent", "content_agent_2", "conclusion_agent"]
            
            for agent_name in agent_order:
                if agent_name in agent_results and agent_results[agent_name]["success"]:
                    agent_result = agent_results[agent_name]
                    section_summaries.append(f"**{agent_name.replace('_', ' ').title()} Summary:**\n{agent_result['summary']}")
            
            # Include any other successful agents not in the order
            for agent_name, result in agent_results.items():
                if agent_name not in agent_order and result["success"]:
                    section_summaries.append(f"**{agent_name.replace('_', ' ').title()} Summary:**\n{result['summary']}")
            
            if not section_summaries:
                return {
                    "success": False,
                    "error": "No successful agent summaries to synthesize"
                }
            
            # Create synthesis prompt
            synthesis_config = self.agents["synthesis_agent"]
            synthesis_prompt = synthesis_config["user_prompt"].format(
                section_summaries="\n\n".join(section_summaries)
            )
            
            # Use LLM Router for synthesis
            print("🔄 Synthesizing final summary...")
            
            synthesis_result = await self.llm_router.route_and_execute(
                text_chunk="",  # No chunk needed for synthesis
                task_type="synthesis",
                system_prompt=synthesis_config["system_prompt"],
                user_prompt=synthesis_prompt
            )
            
            if synthesis_result["success"]:
                print("✅ Final synthesis completed successfully")
                return {
                    "success": True,
                    "content": synthesis_result["content"],
                    "api_used": synthesis_result["api_used"],
                    "model": synthesis_result.get("model", "unknown"),
                    "section_count": len(section_summaries)
                }
            else:
                # Fallback: concatenate summaries
                print("⚠️ Synthesis failed, using fallback concatenation")
                fallback_summary = "\n\n".join(section_summaries)
                return {
                    "success": True,
                    "content": fallback_summary,
                    "api_used": "fallback_concatenation",
                    "model": "none",
                    "section_count": len(section_summaries),
                    "synthesis_error": synthesis_result.get("error")
                }
        
        except Exception as e:
            print(f"❌ Synthesis error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_processing_stats(self, agent_results: Dict, synthesis_result: Dict) -> Dict[str, Any]:
        """
        Compile comprehensive processing statistics
        """
        total_chunks = 0
        successful_chunks = 0
        failed_chunks = 0
        api_usage = {}
        
        # Aggregate agent stats
        for agent_name, result in agent_results.items():
            if "stats" in result:
                stats = result["stats"]
                total_chunks += stats["total_chunks"]
                successful_chunks += stats["successful_chunks"]
                failed_chunks += stats["failed_chunks"]
            
            # Track API usage
            if "chunk_summaries" in result:
                for chunk_summary in result["chunk_summaries"]:
                    api_used = chunk_summary.get("api_used", "unknown")
                    api_usage[api_used] = api_usage.get(api_used, 0) + 1
        
        # Add synthesis API usage
        if synthesis_result.get("api_used"):
            synthesis_api = synthesis_result["api_used"]
            api_usage[synthesis_api] = api_usage.get(synthesis_api, 0) + 1
        
        return {
            "total_chunks_processed": total_chunks,
            "successful_chunks": successful_chunks,
            "failed_chunks": failed_chunks,
            "success_rate": round((successful_chunks / total_chunks) * 100, 1) if total_chunks > 0 else 0,
            "agents_used": len(agent_results),
            "api_usage_breakdown": api_usage,
            "synthesis_successful": synthesis_result.get("success", False)
        }
    
    def print_status(self):
        """Print comprehensive status"""
        print("\n🤖 Enhanced Agentic Summarizer Status")
        print("=" * 50)
        print(f"🔧 Agents configured: {len(self.agents)}")
        print(f"🎯 LLM Router status:")
        self.llm_router.print_status()
        print("=" * 50)
