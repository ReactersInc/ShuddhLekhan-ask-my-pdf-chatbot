"""
Simple status check for the reactive LLM router
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.smart_api_manager import SmartAPIManager
from services.reactive_router_status import ReactiveRouterStatus

# Initialize the system
api_manager = SmartAPIManager()
status_display = ReactiveRouterStatus(api_manager)

# Simulate API keys for demo
for api_name in api_manager.api_configs:
    api_manager.api_configs[api_name]['key'] = f'demo_key_{api_name}'

# Show comprehensive status
status_display.display_live_status()
status_display.display_routing_strategy()
