# =============================================================================
# USER-SPECIFIC LIST ROUTES
# =============================================================================
"""
Enhanced List Routes with User Session Management

This module defines the routes for PDF listing with both authenticated
and non-authenticated access patterns.

Routes:
- GET /pdfs/ - Smart listing (user-specific if authenticated, global if not)
- GET /pdfs/user - User-specific listing (authentication required)
- GET /pdfs/stats - User statistics (authentication required)

Author: [Your Team]
Created for: User-Specific Sessions Implementation
"""

from flask import Blueprint, g
from controllers.list_controller import handle_list_pdfs, handle_authenticated_list_pdfs, get_user_pdf_statistics
from utils.auth_utils import require_auth

list_bp = Blueprint('pdf_list', __name__)

@list_bp.route("/", methods=["GET"])
def list_pdf():
    """
    Smart PDF listing with user context awareness
    
    This endpoint automatically detects if the user is authenticated:
    - If authenticated: Returns user-specific PDF list
    - If not authenticated: Returns global PDF list (legacy behavior)
    
    Optional Headers:
    Authorization: Bearer <jwt_token> (for user-specific results)
    
    Response:
    {
        "status": "success",
        "pdfs": [pdf_list],
        "total_files": count,
        "user_specific": true/false,
        "user_id": "uuid" (if authenticated)
    }
    """
    return handle_list_pdfs()

@list_bp.route("/user", methods=["GET"])
@require_auth  # Explicitly require authentication
def list_user_pdfs():
    """
    User-specific PDF listing (authentication required)
    
    This endpoint always requires authentication and returns only
    the PDFs that belong to the authenticated user.
    
    Headers Required:
    Authorization: Bearer <jwt_token>
    
    Response:
    {
        "status": "success",
        "pdfs": [user_pdf_list],
        "total_files": count,
        "user_id": "uuid",
        "user_specific": true
    }
    """
    return handle_authenticated_list_pdfs()

@list_bp.route("/stats", methods=["GET"])
@require_auth  # Require authentication for statistics
def get_user_statistics():
    """
    Get user's PDF statistics and analytics
    
    This endpoint provides comprehensive statistics about the
    authenticated user's uploaded PDFs and processing status.
    
    Headers Required:
    Authorization: Bearer <jwt_token>
    
    Response:
    {
        "status": "success",
        "statistics": {
            "total_files": count,
            "files_with_summaries": count,
            "pending_summaries": count,
            "total_size_bytes": size,
            "total_size_mb": size_mb
        },
        "user_id": "uuid"
    }
    """
    user_id = g.user_id
    return get_user_pdf_statistics(user_id)

# =============================================================================
# LEGACY COMPATIBILITY ROUTES
# =============================================================================

@list_bp.route("/legacy", methods=["GET"])
def list_all_pdfs_legacy():
    """
    Legacy global PDF listing (non-authenticated)
    
    This endpoint explicitly provides the old global behavior
    for any integrations that specifically need non-user-specific results.
    
    Note: Consider removing this after full migration to user-specific sessions.
    """
    from controllers.list_controller import handle_legacy_pdfs
    return handle_legacy_pdfs()

# =============================================================================
# INTEGRATION NOTES FOR DEVELOPERS
# =============================================================================
"""
Frontend Integration Examples:

1. SMART LISTING (recommended):
   // Without authentication - gets global list
   fetch('/pdfs/')
   
   // With authentication - gets user-specific list
   fetch('/pdfs/', {
       headers: {
           'Authorization': 'Bearer ' + token
       }
   })

2. EXPLICIT USER LISTING:
   fetch('/pdfs/user', {
       headers: {
           'Authorization': 'Bearer ' + token
       }
   })

3. USER STATISTICS:
   fetch('/pdfs/stats', {
       headers: {
           'Authorization': 'Bearer ' + token
       }
   })

Response Handling:
- Check 'user_specific' field to determine if results are filtered
- Use 'user_id' field to identify the authenticated user
- Handle statistics for user dashboard and analytics
- Support both authenticated and non-authenticated modes

Migration Benefits:
- Existing integrations continue to work unchanged
- New authenticated clients get user-specific results automatically
- Gradual migration path to full user-based sessions
- Backward compatibility maintained throughout transition
"""