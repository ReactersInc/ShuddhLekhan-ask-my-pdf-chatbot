"""
Quick test script for the Enhanced LLM Router integration
"""
import sys
import os

# Add parent directory to path so we can import from services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.agentic_summarizer import AgenticSummarizer

def test_enhanced_summarizer():
    """Test the enhanced agentic summarizer"""
    
    # Sample PDF content to test
    test_content = """
    Introduction to Artificial Intelligence
    
    Artificial Intelligence (AI) represents one of the most significant technological advances of our time. This field encompasses the development of computer systems capable of performing tasks that traditionally require human intelligence.
    
    The core concepts of AI include machine learning, neural networks, and deep learning. Machine learning algorithms enable computers to learn from data without explicit programming. Neural networks simulate the way human brains process information through interconnected nodes.
    
    Applications of AI span across various industries including healthcare, finance, transportation, and entertainment. In healthcare, AI assists in medical diagnosis and drug discovery. Financial institutions use AI for fraud detection and algorithmic trading.
    
    Future prospects of AI include the development of artificial general intelligence and quantum computing integration. These advances will likely revolutionize how we interact with technology and solve complex problems.
    
    In conclusion, artificial intelligence continues to evolve and transform our world. The potential benefits are enormous, but we must also consider ethical implications and ensure responsible development of these powerful technologies.
    """
    
    try:
        print("🧪 Testing Enhanced Agentic Summarizer")
        print("=" * 50)
        
        # Initialize the summarizer
        summarizer = AgenticSummarizer()
        
        # Check if router is enabled
        if hasattr(summarizer, 'use_router') and summarizer.use_router:
            print("✅ LLM Router is ENABLED")
            print(f"🔧 Available APIs: {len(summarizer.api_manager._get_available_apis())}")
            summarizer.api_manager.print_status()
        else:
            print("⚠️ LLM Router is DISABLED - using fallback single LLM")
        
        print("\n🚀 Starting test summarization...")
        print("-" * 50)
        
        # Run summarization
        result = summarizer.fast_summarize(test_content, "test_ai_document.pdf")
        
        print("\n📊 Results:")
        print("=" * 50)
        print(f"✅ Status: {result.get('status', 'unknown')}")
        print(f"⏱️ Processing time: {result.get('processing_time', 0)} seconds")
        print(f"📄 Chunks processed: {result.get('chunks_processed', 0)}")
        print(f"🤖 Method: {result.get('method', 'unknown')}")
        
        if 'router_stats' in result:
            print(f"🎯 Router used: YES")
            router_stats = result['router_stats']
            print(f"📈 Total API calls: {router_stats.get('total_calls', 0)}")
            print(f"✅ Success rate: {router_stats.get('successful_calls', 0)}/{router_stats.get('total_calls', 0)}")
        
        print(f"\n📝 Summary Preview:")
        print("-" * 30)
        summary = result.get('summary', 'No summary generated')
        print(summary[:300] + "..." if len(summary) > 300 else summary)
        
        print("\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_summarizer()
    sys.exit(0 if success else 1)
