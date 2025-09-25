# =============================================================================
# USER-SPECIFIC LIST CONTROLLER
# =============================================================================
"""
Enhanced List Controller with User Session Management

This controller handles both user-specific file listings and legacy
global listings, providing a smooth transition to user-based sessions.

Features:
- User-specific PDF listings with authentication
- Legacy global listings for backward compatibility
- Summary integration and file statistics
- Secure user-scoped data access

Author: [Your Team]
Created for: User-Specific Sessions Implementation
"""

from flask import jsonify, g
from services.list_service import get_all_pdf_with_summaries, get_user_pdfs_with_summaries, get_user_file_count

def handle_list_pdfs():
    """
    Handle PDF listing with user context awareness
    
    This function checks if a user is authenticated and returns either:
    1. User-specific PDF list (if authenticated)
    2. Global PDF list (if not authenticated - legacy behavior)
    
    Returns:
        JSON response with PDF list and user context
    """
    user_id = getattr(g, 'user_id', None)  # Get user_id from auth decorator if present
    
    if user_id:
        # User is authenticated - return user-specific list
        return handle_user_pdfs(user_id)
    else:
        # No authentication - return legacy global list
        return handle_legacy_pdfs()

def handle_user_pdfs(user_id):
    """
    Handle authenticated user's PDF listing
    
    This function returns only the PDFs that belong to the authenticated
    user, providing user-specific session management.
    
    Args:
        user_id: UUID of the authenticated user
    
    Returns:
        JSON response with user's PDF list and statistics
    """
    try:
        pdfs = get_user_pdfs_with_summaries(user_id)
        file_count = get_user_file_count(user_id)
        
        return jsonify({
            'status': 'success',
            'pdfs': pdfs,
            'total_files': file_count,
            'user_id': user_id,
            'user_specific': True,
            'message': f'Found {len(pdfs)} PDFs for user'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve user PDFs: {str(e)}',
            'user_specific': True
        }), 500

def handle_legacy_pdfs():
    """
    Handle legacy global PDF listing (non-authenticated)
    
    This function maintains backward compatibility for existing
    integrations that don't use authentication yet.
    
    Returns:
        JSON response with global PDF list
    """
    try:
        pdfs = get_all_pdf_with_summaries()
        
        return jsonify({
            'status': 'success',
            'pdfs': pdfs,
            'total_files': len(pdfs),
            'user_specific': False,
            'message': f'Found {len(pdfs)} PDFs (global view)'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve PDFs: {str(e)}',
            'user_specific': False
        }), 500

def handle_authenticated_list_pdfs():
    """
    Explicitly handle authenticated PDF listing
    
    This function is designed to be used with @require_auth decorator
    to ensure user authentication is required.
    
    Returns:
        JSON response with authenticated user's PDF list
    """
    user_id = g.user_id  # This will be available due to @require_auth
    return handle_user_pdfs(user_id)

def get_user_pdf_statistics(user_id):
    """
    Get comprehensive statistics for user's PDFs
    
    Args:
        user_id: UUID of the authenticated user
    
    Returns:
        JSON response with user's PDF statistics
    """
    try:
        pdfs = get_user_pdfs_with_summaries(user_id)
        
        # Calculate statistics
        total_files = len(pdfs)
        files_with_summaries = len([pdf for pdf in pdfs if pdf['summary_status'] == 'completed'])
        pending_summaries = total_files - files_with_summaries
        total_size = sum(pdf.get('file_size', 0) for pdf in pdfs if pdf.get('file_size'))
        
        return jsonify({
            'status': 'success',
            'statistics': {
                'total_files': total_files,
                'files_with_summaries': files_with_summaries,
                'pending_summaries': pending_summaries,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2) if total_size else 0
            },
            'user_id': user_id
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get statistics: {str(e)}'
        }), 500

# =============================================================================
# USAGE NOTES FOR DEVELOPERS
# =============================================================================
"""
Integration with Routes:

1. FLEXIBLE ROUTE (supports both authenticated and non-authenticated):
   @list_bp.route("/", methods=["GET"])
   def list_pdf():
       return handle_list_pdfs()  # Auto-detects authentication

2. AUTHENTICATED-ONLY ROUTE:
   @list_bp.route("/user", methods=["GET"])
   @require_auth
   def list_user_pdf():
       return handle_authenticated_list_pdfs()

3. STATISTICS ROUTE:
   @list_bp.route("/stats", methods=["GET"])
   @require_auth
   def get_stats():
       return get_user_pdf_statistics(g.user_id)

Frontend Integration:
- Include Authorization header for user-specific results
- Handle both user_specific: true/false in responses
- Display user context and statistics
- Support both authenticated and non-authenticated modes

Migration Strategy:
- Existing API calls work unchanged (legacy mode)
- New authenticated calls get user-specific results
- Gradual migration to full user-based session management
- No breaking changes to current integrations
"""