from flask import Blueprint, request, jsonify
from controllers.enhanced_summarize_controller import enhanced_summarize_controller

# Create blueprint for enhanced summarization routes
enhanced_summarize_bp = Blueprint('enhanced_summarize', __name__)

@enhanced_summarize_bp.route('/api/enhanced/summarize', methods=['POST'])
def enhanced_summarize():
    """
    Enhanced summarization endpoint with LLM Router
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        chunks = data.get('chunks', [])
        document_info = data.get('document_info', {})
        
        if not chunks:
            return jsonify({
                "success": False,
                "error": "No chunks provided for summarization"
            }), 400
        
        # Execute enhanced summarization
        result = enhanced_summarize_controller.summarize_chunks(chunks, document_info)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@enhanced_summarize_bp.route('/api/enhanced/router/status', methods=['GET'])
def get_router_status():
    """
    Get LLM Router status and statistics
    """
    try:
        result = enhanced_summarize_controller.get_router_status()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@enhanced_summarize_bp.route('/api/enhanced/router/test', methods=['POST'])
def test_router():
    """
    Test LLM Router connectivity
    """
    try:
        result = enhanced_summarize_controller.test_router_connection()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@enhanced_summarize_bp.route('/api/enhanced/router/reset/<api_name>', methods=['POST'])
def emergency_reset_api(api_name):
    """
    Emergency reset for specific API
    """
    try:
        result = enhanced_summarize_controller.emergency_reset_api(api_name)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@enhanced_summarize_bp.route('/api/enhanced/info', methods=['GET'])
def get_enhanced_info():
    """
    Get information about enhanced summarization system
    """
    return jsonify({
        "success": True,
        "system_info": {
            "name": "Enhanced Agentic Summarizer with LLM Router",
            "version": "1.0.0",
            "features": [
                "Multi-API routing with 5 APIs",
                "Intelligent complexity analysis",
                "Language-aware routing (Hindi/Urdu/Bengali support)",
                "Agentic summarization with specialized agents",
                "Smart load balancing",
                "Emergency failover",
                "Rate limit management"
            ],
            "supported_apis": [
                "Google Gemma (Primary & Secondary)",
                "GROQ",
                "Together AI", 
                "OpenRouter"
            ],
            "agents": [
                "Introduction Agent",
                "Content Agent", 
                "Conclusion Agent",
                "Synthesis Agent"
            ]
        }
    }), 200
