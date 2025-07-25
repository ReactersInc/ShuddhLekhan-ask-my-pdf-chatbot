"""
Reactive LLM Router Status Display
Enhanced status monitoring for the reactive API management system
"""

import time
from typing import Dict, List
from .smart_api_manager import SmartAPIManager


class ReactiveRouterStatus:
    """Displays real-time status of the reactive LLM router"""
    
    def __init__(self, api_manager: SmartAPIManager):
        self.api_manager = api_manager
    
    def display_live_status(self):
        """Display live status of all APIs"""
        print("\n" + "="*80)
        print("🎯 REACTIVE LLM ROUTER - LIVE STATUS")
        print("="*80)
        
        current_time = time.time()
        total_apis = len(self.api_manager.api_configs)
        available_count = 0
        
        for api_name, config in self.api_manager.api_configs.items():
            if not config['key']:
                print(f"❌ {api_name:15} | NO API KEY CONFIGURED")
                continue
            
            stats = self.api_manager.usage_stats[api_name]
            is_available = self.api_manager._is_api_currently_available(api_name)
            
            if is_available:
                available_count += 1
                status_icon = "🟢"
                status_text = "READY"
                extra_info = ""
            else:
                status_icon = "🔴"
                if stats.rate_limit_reset_time > current_time:
                    cooldown_remaining = int(stats.rate_limit_reset_time - current_time)
                    status_text = f"COOLDOWN"
                    extra_info = f"({cooldown_remaining}s remaining)"
                else:
                    status_text = "ERROR"
                    extra_info = "(check logs)"
            
            # Statistics
            success_rate = 0
            if stats.calls_made > 0:
                success_rate = (stats.successful_calls / stats.calls_made) * 100
            
            provider = config.get('provider', 'unknown')
            priority = config.get('priority', 999)
            
            print(f"{status_icon} {api_name:15} | {status_text:10} {extra_info:15} | "
                  f"Provider: {provider:10} | Priority: {priority:2} | "
                  f"Calls: {stats.calls_made:3} | Success: {success_rate:5.1f}%")
            
            # Show last error if exists and API is not available
            if not is_available and stats.last_error:
                error_preview = stats.last_error[:60] + "..." if len(stats.last_error) > 60 else stats.last_error
                print(f"   └─ Last Error: {error_preview}")
        
        print("-" * 80)
        print(f"📊 SUMMARY: {available_count}/{total_apis} APIs Available")
        
        if available_count == 0:
            print("🚨 WARNING: No APIs currently available!")
            print("   • Check API keys in environment variables")
            print("   • Verify rate limits haven't been exceeded")
            print("   • Consider using emergency reset if needed")
        elif available_count < total_apis:
            print(f"⚠️  NOTICE: {total_apis - available_count} API(s) in cooldown")
            print("   • System will automatically retry when cooldown expires")
            print("   • Other APIs will handle requests in the meantime")
        else:
            print("✅ EXCELLENT: All APIs ready for requests")
        
        print("="*80)
        print("🔄 Strategy: Reactive switching • Google APIs prioritized • Automatic fallbacks")
        print("="*80)
    
    def display_routing_strategy(self):
        """Display the routing strategy explanation"""
        print("\n" + "="*70)
        print("🧠 REACTIVE ROUTING STRATEGY")
        print("="*70)
        
        print("📋 CONTENT ANALYSIS:")
        print("   • Hindi/Urdu/Bengali detection → Google APIs priority")
        print("   • Complexity analysis → High complexity → Google APIs")
        print("   • Technical content → Preferred powerful models")
        print()
        
        print("🎯 API SELECTION LOGIC:")
        print("   1. Indic Scripts → Must use Google APIs")
        print("   2. High Complexity → Google > Together AI > GROQ > OpenRouter")
        print("   3. Medium Complexity → Smart balance between Google APIs")
        print("   4. Low Complexity → Any available API")
        print()
        
        print("🚫 RATE LIMIT HANDLING:")
        print("   • React to HTTP 429/400/403 responses")
        print("   • Immediate cooldown based on error type")
        print("   • RPM limits → 70s cooldown")
        print("   • Daily limits → 1 hour cooldown") 
        print("   • Auth errors → 30 min cooldown")
        print()
        
        print("🔄 FALLBACK CHAIN:")
        print("   • Rate limit hit → Switch to next priority API")
        print("   • Google Primary → Google Secondary → Together AI → GROQ → OpenRouter")
        print("   • Maintain Indic script preference throughout")
        print()
        
        print("⚡ ADVANTAGES:")
        print("   ✓ No artificial daily limits")
        print("   ✓ Real-time rate limit detection")
        print("   ✓ Language-aware routing")
        print("   ✓ Intelligent load balancing")
        print("   ✓ Automatic recovery from errors")
        print("="*70)
    
    def display_api_details(self):
        """Display detailed API configuration"""
        print("\n" + "="*90)
        print("⚙️  API CONFIGURATION DETAILS")
        print("="*90)
        
        for api_name, config in self.api_manager.api_configs.items():
            has_key = "✓" if config['key'] else "✗"
            provider = config.get('provider', 'Unknown')
            priority = config.get('priority', 999)
            delay = config.get('delay_between_calls', 1)
            
            print(f"🔧 {api_name.upper()}")
            print(f"   Provider: {provider}")
            print(f"   Priority: {priority} (lower = higher priority)")
            print(f"   API Key: {has_key}")
            print(f"   Delay Between Calls: {delay}s")
            
            # Real limits from Google documentation
            if api_name.startswith('google'):
                print(f"   Known Limits: 1500 requests/day, 15 RPM, 1M TPM")
            elif api_name == 'groq':
                print(f"   Known Limits: Varies by model, typically high RPM")
            elif api_name == 'together_ai':
                print(f"   Known Limits: Varies by subscription tier")
            elif api_name == 'openrouter':
                print(f"   Known Limits: Depends on underlying model")
            
            print()
        
        print("="*90)
    
    def show_recent_activity(self, last_n_minutes: int = 10):
        """Show recent API activity"""
        print(f"\n📈 RECENT ACTIVITY (Last {last_n_minutes} minutes)")
        print("-" * 50)
        
        current_time = time.time()
        cutoff_time = current_time - (last_n_minutes * 60)
        
        for api_name, stats in self.api_manager.usage_stats.items():
            if stats.last_call_time > cutoff_time:
                time_ago = int(current_time - stats.last_call_time)
                if time_ago < 60:
                    time_str = f"{time_ago}s ago"
                else:
                    time_str = f"{time_ago//60}m ago"
                
                status = "✅ SUCCESS" if stats.last_error is None else "❌ FAILED"
                print(f"{api_name:15} | {time_str:8} | {status}")
                
                if stats.last_error:
                    error_preview = stats.last_error[:40] + "..." if len(stats.last_error) > 40 else stats.last_error
                    print(f"{'':15} | {'':8} | Error: {error_preview}")
        
        print("-" * 50)
    
    def emergency_dashboard(self):
        """Emergency control dashboard"""
        print("\n" + "🚨" * 20)
        print("EMERGENCY CONTROL DASHBOARD")
        print("🚨" * 20)
        
        print("\nAvailable Emergency Actions:")
        print("1. Force enable all APIs: api_manager.force_enable_all_apis()")
        print("2. Reset specific API: api_manager.emergency_reset('api_name')")
        print("3. Check configuration: api_manager.print_status()")
        
        total_available = len(self.api_manager.get_available_apis())
        total_configured = len([k for k, v in self.api_manager.api_configs.items() if v['key']])
        
        if total_available == 0:
            print("\n🚨 CRITICAL: No APIs available!")
            print("Recommended action: api_manager.force_enable_all_apis()")
        elif total_available < total_configured:
            print(f"\n⚠️  {total_configured - total_available} APIs in cooldown")
            print("System can continue with available APIs")
        
        print("🚨" * 20)


def quick_status_check(api_manager: SmartAPIManager):
    """Quick one-line status check"""
    available = len(api_manager.get_available_apis())
    total = len([k for k, v in api_manager.api_configs.items() if v['key']])
    
    if available == total:
        print(f"✅ All {total} APIs ready")
    elif available > 0:
        print(f"⚠️  {available}/{total} APIs available")
    else:
        print("🚨 No APIs available!")
    
    return available, total
