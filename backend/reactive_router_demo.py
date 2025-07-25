"""
Reactive LLM Router Test Script
Demonstrates the reactive API management system without requiring real API keys
"""

import os
import sys
import time
from typing import Dict

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.smart_api_manager import SmartAPIManager
from services.chunk_complexity_analyzer import ChunkComplexityAnalyzer
from services.reactive_router_status import ReactiveRouterStatus, quick_status_check


def simulate_api_responses():
    """Simulate different API response scenarios"""
    print("🧪 REACTIVE LLM ROUTER DEMONSTRATION")
    print("="*60)
    print("This demo shows how the reactive system handles different scenarios")
    print("without requiring actual API keys.\n")
    
    # Initialize components
    api_manager = SmartAPIManager()
    complexity_analyzer = ChunkComplexityAnalyzer()
    status_display = ReactiveRouterStatus(api_manager)
    
    # Simulate API keys for demo
    api_manager.api_configs['google_primary']['key'] = 'demo_key_1'
    api_manager.api_configs['google_secondary']['key'] = 'demo_key_2'
    api_manager.api_configs['groq']['key'] = 'demo_key_3'
    api_manager.api_configs['together_ai']['key'] = 'demo_key_4'
    api_manager.api_configs['openrouter']['key'] = 'demo_key_5'
    
    print("1️⃣  INITIAL STATUS - All APIs Ready")
    status_display.display_live_status()
    input("\nPress Enter to continue...")
    
    # Scenario 1: English content
    print("\n2️⃣  SCENARIO: English Technical Content")
    english_content = """
    Machine learning algorithms have revolutionized the field of artificial intelligence.
    Deep learning networks, particularly convolutional neural networks, have shown 
    remarkable performance in computer vision tasks.
    """
    
    analysis = complexity_analyzer.analyze_chunk(english_content)
    print(f"📊 Complexity Analysis: {analysis}")
    
    best_api = api_manager.get_best_api(analysis)
    print(f"🎯 Selected API: {best_api}")
    
    input("\nPress Enter to continue...")
    
    # Scenario 2: Hindi content
    print("\n3️⃣  SCENARIO: Hindi Content (Indic Script Priority)")
    hindi_content = """
    मशीन लर्निंग एक महत्वपूर्ण तकनीक है जो कृत्रिम बुद्धिमत्ता के क्षेत्र में
    क्रांति ला रही है। डीप लर्निंग नेटवर्क विशेष रूप से कंप्यूटर विज़न में
    उत्कृष्ट परिणाम दे रहे हैं।
    """
    
    analysis = complexity_analyzer.analyze_chunk(hindi_content)
    print(f"📊 Complexity Analysis: {analysis}")
    
    best_api = api_manager.get_best_api(analysis)
    print(f"🎯 Selected API: {best_api} (Google prioritized for Indic script)")
    
    input("\nPress Enter to continue...")
    
    # Scenario 3: Simulate rate limit hit
    print("\n4️⃣  SCENARIO: Rate Limit Hit - Reactive Switching")
    print("Simulating rate limit error on Google Primary...")
    
    # Simulate rate limit error
    api_manager.record_api_call('google_primary', False, 
                               "429 Too Many Requests: Quota exceeded for requests per minute")
    
    status_display.display_live_status()
    
    # Try to get API again - should fallback
    best_api = api_manager.get_best_api(analysis)
    print(f"🔄 After rate limit, selected API: {best_api}")
    
    input("\nPress Enter to continue...")
    
    # Scenario 4: Multiple failures
    print("\n5️⃣  SCENARIO: Multiple API Failures")
    print("Simulating failures on multiple APIs...")
    
    api_manager.record_api_call('google_secondary', False, 
                               "503 Service Temporarily Unavailable")
    api_manager.record_api_call('groq', False, 
                               "Authentication failed: Invalid API key")
    
    status_display.display_live_status()
    
    # Show available APIs
    available = api_manager.get_available_apis()
    print(f"📋 Still available APIs: {available}")
    
    input("\nPress Enter to continue...")
    
    # Scenario 5: Emergency reset
    print("\n6️⃣  SCENARIO: Emergency Recovery")
    print("Forcing all APIs back online...")
    
    api_manager.force_enable_all_apis()
    status_display.display_live_status()
    
    input("\nPress Enter to continue...")
    
    # Show routing strategy
    print("\n7️⃣  ROUTING STRATEGY EXPLANATION")
    status_display.display_routing_strategy()
    
    input("\nPress Enter to continue...")
    
    # Show API details
    print("\n8️⃣  API CONFIGURATION DETAILS")
    status_display.display_api_details()
    
    print("\n✅ DEMO COMPLETE!")
    print("="*60)
    print("🎯 KEY BENEFITS OF REACTIVE APPROACH:")
    print("   ✓ No artificial daily limits - reacts to real API responses")
    print("   ✓ Immediate fallback when rate limits hit")
    print("   ✓ Language-aware routing for better results")
    print("   ✓ Google APIs prioritized for Indic languages")
    print("   ✓ Automatic recovery after cooldown periods")
    print("   ✓ Intelligent load balancing between APIs")
    print("="*60)


def quick_test():
    """Quick test of the reactive system"""
    print("⚡ QUICK REACTIVE ROUTER TEST")
    print("-" * 40)
    
    # Setup
    api_manager = SmartAPIManager()
    complexity_analyzer = ChunkComplexityAnalyzer()
    
    # Simulate API keys
    for api_name in api_manager.api_configs:
        api_manager.api_configs[api_name]['key'] = f'demo_key_{api_name}'
    
    # Test different content types
    test_cases = [
        ("English Tech", "Machine learning algorithms optimize neural networks."),
        ("Hindi Text", "मशीन लर्निंग एक महत्वपूर्ण तकनीक है।"),
        ("Complex Code", "def optimize_transformer_attention(q, k, v, mask=None): return scaled_dot_product_attention(q, k, v, mask)")
    ]
    
    for name, content in test_cases:
        print(f"\n📝 {name}:")
        analysis = complexity_analyzer.analyze_chunk(content)
        best_api = api_manager.get_best_api(analysis)
        print(f"   Language: {analysis.get('language', 'unknown')}")
        print(f"   Complexity: {analysis.get('complexity', 'unknown')}")
        print(f"   Selected API: {best_api}")
        print(f"   Has Indic Script: {analysis.get('has_indic_script', False)}")
    
    print("\n" + "-" * 40)
    quick_status_check(api_manager)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Reactive LLM Router Demo")
    parser.add_argument("--quick", action="store_true", help="Run quick test")
    parser.add_argument("--full", action="store_true", help="Run full demo")
    
    args = parser.parse_args()
    
    if args.quick:
        quick_test()
    elif args.full:
        simulate_api_responses()
    else:
        print("Choose --quick for quick test or --full for complete demo")
        print("Example: python reactive_router_demo.py --quick")
