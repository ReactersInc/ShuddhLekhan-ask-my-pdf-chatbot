import asyncio
from typing import List, Dict, Any
from flask import jsonify
from services.enhanced_agentic_summarizer import EnhancedAgenticSummarizer

class EnhancedSummarizeController:
    """
    Controller for enhanced agentic summarization with LLM Router
    """
    
    def __init__(self):
        self.summarizer = EnhancedAgenticSummarizer()
    
    def summarize_chunks(self, chunks: List[str], document_info: Dict = None) -> Dict[str, Any]:
        """
        Main endpoint for enhanced summarization
        """
        try:
            if not chunks:
                return {
                    "success": False,
                    "error": "No chunks provided for summarization"
                }
            
            print(f"🚀 Starting enhanced summarization for {len(chunks)} chunks")
            
            # Run async summarization in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.summarizer.summarize_document(chunks)
                )
            finally:
                loop.close()
            
            # Add document info if provided
            if document_info:
                result["document_info"] = document_info
            
            # Add timestamp
            import datetime
            result["processing_timestamp"] = datetime.datetime.now().isoformat()
            
            print("✅ Enhanced summarization completed")
            return result
            
        except Exception as e:
            print(f"❌ Error in enhanced summarization controller: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "routing_stats": self.summarizer.llm_router.get_routing_stats() if hasattr(self.summarizer, 'llm_router') else {}
            }
    
    def get_router_status(self) -> Dict[str, Any]:
        """
        Get current LLM Router status
        """
        try:
            return {
                "success": True,
                "routing_stats": self.summarizer.llm_router.get_routing_stats(),
                "api_status": self.summarizer.llm_router.api_manager.get_usage_summary()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def emergency_reset_api(self, api_name: str) -> Dict[str, Any]:
        """
        Emergency reset for specific API
        """
        try:
            self.summarizer.llm_router.api_manager.emergency_reset(api_name)
            return {
                "success": True,
                "message": f"Emergency reset completed for {api_name}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_router_connection(self) -> Dict[str, Any]:
        """
        Test connection to all APIs
        """
        try:
            # Simple test text
            test_text = "This is a test to verify API connectivity."
            
            # Run test with each available API
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.summarizer.llm_router.route_and_execute(
                        text_chunk=test_text,
                        task_type="summarize"
                    )
                )
            finally:
                loop.close()
            
            return {
                "success": True,
                "test_result": result,
                "router_stats": self.summarizer.llm_router.get_routing_stats()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
enhanced_summarize_controller = EnhancedSummarizeController()
