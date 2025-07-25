"""
Test the improved LLM Router with better error handling and fallbacks
"""
import sys
import os
import asyncio

# Add parent directory to path so we can import from services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.agentic_summarizer import AgenticSummarizer

def test_quota_handling():
    """Test how the system handles quota exceeded errors"""
    
    # Longer test content to trigger more API calls
    test_content = """
    Chapter 1: Introduction to Advanced Machine Learning
    
    Machine learning has evolved significantly in recent years, with deep learning architectures revolutionizing fields from computer vision to natural language processing. This comprehensive guide explores cutting-edge techniques and their practical applications.
    
    The fundamental concepts include supervised learning, unsupervised learning, and reinforcement learning. Each paradigm offers unique advantages for different problem domains. Supervised learning excels in classification and regression tasks where labeled data is abundant.
    
    Chapter 2: Neural Network Architectures
    
    Convolutional Neural Networks (CNNs) have transformed image processing and computer vision tasks. Their hierarchical feature extraction capabilities enable automatic learning of visual patterns from raw pixel data. Key innovations include skip connections, attention mechanisms, and batch normalization.
    
    Recurrent Neural Networks (RNNs) and their variants like LSTM and GRU excel in sequential data processing. These architectures maintain internal memory states, making them suitable for time series analysis, natural language processing, and speech recognition applications.
    
    Chapter 3: Transformer Architecture
    
    The transformer architecture introduced the concept of self-attention, enabling parallel processing of sequences and capturing long-range dependencies more effectively than RNNs. This breakthrough led to the development of large language models like BERT, GPT, and T5.
    
    Multi-head attention mechanisms allow the model to focus on different aspects of the input simultaneously. Position encodings provide sequence order information, while layer normalization and residual connections ensure stable training of deep networks.
    
    Chapter 4: Transfer Learning and Fine-tuning
    
    Transfer learning leverages pre-trained models to solve related tasks with limited data. This approach significantly reduces training time and computational requirements while often achieving superior performance compared to training from scratch.
    
    Fine-tuning strategies include freezing early layers, gradual unfreezing, and domain adaptation techniques. The choice of strategy depends on the similarity between source and target domains, as well as the amount of available target data.
    
    Chapter 5: Optimization and Regularization
    
    Modern optimization algorithms like Adam, RMSprop, and AdamW incorporate adaptive learning rates and momentum to accelerate convergence. Learning rate scheduling and warm-up strategies further improve training stability and final model performance.
    
    Regularization techniques prevent overfitting and improve generalization. Methods include dropout, batch normalization, weight decay, and data augmentation. Early stopping and cross-validation help select optimal model complexity.
    
    Chapter 6: Deployment and Production
    
    Model deployment requires consideration of latency, throughput, and resource constraints. Techniques like quantization, pruning, and knowledge distillation reduce model size and inference time while maintaining accuracy.
    
    Production systems must handle model versioning, A/B testing, and continuous monitoring. MLOps practices ensure reliable, scalable, and maintainable machine learning applications in real-world environments.
    
    Conclusion
    
    Advanced machine learning continues to evolve rapidly, with new architectures and techniques emerging regularly. Success in this field requires continuous learning, experimentation, and adaptation to new developments while maintaining focus on practical applications and real-world impact.
    """
    
    try:
        print("🧪 Testing Enhanced LLM Router with Quota Handling")
        print("=" * 60)
        print(f"📄 Test content length: {len(test_content)} characters")
        
        # Initialize the summarizer
        summarizer = AgenticSummarizer()
        
        # Check router status
        if hasattr(summarizer, 'use_router') and summarizer.use_router:
            print("✅ LLM Router is ENABLED")
            summarizer.api_manager.print_status()
        else:
            print("⚠️ LLM Router is DISABLED - using fallback single LLM")
        
        print("\n🚀 Starting test summarization with quota handling...")
        print("-" * 60)
        
        # Run summarization
        result = summarizer.fast_summarize(test_content, "test_ml_guide.pdf")
        
        print("\n📊 Results:")
        print("=" * 60)
        print(f"✅ Status: {result.get('status', 'unknown')}")
        print(f"⏱️ Processing time: {result.get('processing_time', 0)} seconds")
        print(f"📄 Chunks processed: {result.get('chunks_processed', 0)}")
        print(f"🤖 Method: {result.get('method', 'unknown')}")
        
        if 'router_stats' in result:
            print(f"🎯 Router used: YES")
            router_stats = result['router_stats']
            print(f"📈 Total API calls: {router_stats.get('total_calls', 0)}")
            print(f"✅ Success rate: {router_stats.get('successful_calls', 0)}/{router_stats.get('total_calls', 0)}")
            
            # Show API breakdown
            if 'api_breakdown' in router_stats:
                print("\n🔧 API Usage Breakdown:")
                for api_name, stats in router_stats['api_breakdown'].items():
                    status = "🟢" if stats['is_available'] else "🔴"
                    print(f"  {status} {api_name}: {stats['calls_made']}/{stats['daily_limit']} calls ({stats['usage_percentage']}%)")
                    if stats.get('last_error'):
                        print(f"      Last error: {stats['last_error'][:100]}...")
        
        print(f"\n📝 Summary Preview:")
        print("-" * 30)
        summary = result.get('summary', 'No summary generated')
        print(summary[:500] + "..." if len(summary) > 500 else summary)
        
        # Test router status after processing
        print(f"\n🔍 Router Status After Processing:")
        if hasattr(summarizer, 'api_manager'):
            summarizer.api_manager.print_status()
        
        print(f"\n🎉 Quota handling test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Testing Enhanced LLM Router with Intelligent Fallbacks")
    print("📊 This test should handle quota exceeded errors gracefully")
    print("🔄 It will try multiple APIs and fallback methods\n")
    
    success = test_quota_handling()
    sys.exit(0 if success else 1)
