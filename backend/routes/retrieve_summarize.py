from flask import Blueprint, jsonify
import os

summarize_bp = Blueprint("summarize", __name__)
SUMMARY_FOLDER = "summaries"

@summarize_bp.route('/<pdf_name>', methods=['GET'])
def get_summary(pdf_name):
    base_name = os.path.splitext(pdf_name)[0]  # removes '.pdf' 
    summary_path = os.path.join(SUMMARY_FOLDER, f"{base_name}.txt")

    if os.path.exists(summary_path):
        with open(summary_path, "r") as f:
            summary = f.read()
        return jsonify({"pdf": pdf_name, "summary": summary})
    else:
        return jsonify({"error": "Summary not found"}), 404

@summarize_bp.route('/router/status', methods=['GET'])
def get_router_status():
    """
    Get LLM Router status from the enhanced AgenticSummarizer
    """
    try:
        from services.agentic_summarizer import AgenticSummarizer
        
        # Create temporary instance to check router status
        summarizer = AgenticSummarizer()
        
        if hasattr(summarizer, 'use_router') and summarizer.use_router:
            router_stats = summarizer.api_manager.get_usage_summary()
            return jsonify({
                "success": True,
                "router_enabled": True,
                "router_stats": router_stats
            }), 200
        else:
            return jsonify({
                "success": True,
                "router_enabled": False,
                "message": "Using single LLM fallback"
            }), 200
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
