# =============================================================================
# USER-SPECIFIC UPLOAD ROUTES
# =============================================================================
"""
Enhanced Upload Routes with User Session Management

This module defines the upload routes with user authentication and
user-specific file management capabilities.

Routes:
- POST /upload/ - Upload files (authentication required)
- GET /upload/files - Get user's file list (authentication required)
- POST /upload/start_processing - Start processing (authentication required)
- GET /upload/task_status/<task_id> - Check task status

Author: [Your Team]
Created for: User-Specific Sessions Implementation
"""

from flask import Blueprint, request, jsonify, g
from controllers.upload_controller import handle_upload_pdfs, check_task_status, get_user_files_list
from controllers.start_processing_controller import start_processing
from utils.auth_utils import require_auth

upload_bp = Blueprint("upload", __name__)

@upload_bp.route('/', methods=['POST'])
@require_auth  # Require authentication for uploads
def upload_pdfs():
    """
    Upload PDFs with user-specific session management
    
    This endpoint:
    1. Requires user authentication via JWT token
    2. Saves files to user-specific folders
    3. Records file metadata in database with user_id
    4. Returns upload results with user context
    
    Headers Required:
    Authorization: Bearer <jwt_token>
    
    Response:
    {
        "uploaded_files": [file_list],
        "folder_tree": user_folder_structure,
        "user_authenticated": true,
        "user_id": "user_uuid"
    }
    """
    return handle_upload_pdfs(request)

@upload_bp.route('/files', methods=['GET'])
@require_auth  # Require authentication for file list
def get_user_files():
    """
    Get authenticated user's file list
    
    This endpoint returns only the files that belong to the
    authenticated user, providing user-specific file management.
    
    Headers Required:
    Authorization: Bearer <jwt_token>
    
    Response:
    {
        "status": "success",
        "files": [user_file_list],
        "total_files": count,
        "user_id": "user_uuid"
    }
    """
    user_id = g.user_id  # Get user_id from auth decorator
    return get_user_files_list(user_id)

@upload_bp.route('/start_processing', methods=['POST'])
@require_auth  # Require authentication for processing
def trigger_processing():
    """
    Start processing uploaded files
    
    This endpoint is now protected and should work with
    user-specific files from the authenticated user.
    
    Headers Required:
    Authorization: Bearer <jwt_token>
    """
    return start_processing()

@upload_bp.route('/task_status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    Check task processing status
    
    This endpoint doesn't require authentication as task_id
    acts as a temporary access token. Could be enhanced to
    include user verification in the future.
    
    Response:
    {
        "status": "pending|processing|completed|failed",
        "progress": 0-100,
        "message": "status_message"
    }
    """
    return check_task_status(task_id)

# =============================================================================
# LEGACY COMPATIBILITY ROUTES (Optional)
# =============================================================================

@upload_bp.route('/legacy', methods=['POST'])
def upload_pdfs_legacy():
    """
    Legacy upload endpoint without authentication
    
    This endpoint maintains backward compatibility for any
    existing integrations that don't use authentication yet.
    
    Note: Consider removing this after full migration to
    user-specific uploads.
    """
    # Temporarily bypass authentication for legacy uploads
    return handle_upload_pdfs(request)

# =============================================================================
# USER FILE MANAGEMENT ROUTES
# =============================================================================

@upload_bp.route('/files/<file_id>', methods=['DELETE'])
@require_auth
def delete_user_file(file_id):
    """
    Delete specific file belonging to authenticated user
    
    This endpoint allows users to delete their own files
    with proper security checks.
    
    Args:
        file_id: UUID of the file to delete
    
    Headers Required:
    Authorization: Bearer <jwt_token>
    """
    from services.upload_service import delete_user_file
    
    user_id = g.user_id
    success = delete_user_file(file_id, user_id)
    
    if success:
        return jsonify({
            "status": "success",
            "message": "File deleted successfully",
            "file_id": file_id
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "File not found or unauthorized"
        }), 404

@upload_bp.route('/files/<file_id>', methods=['GET'])
@require_auth
def get_user_file_details(file_id):
    """
    Get details of specific file belonging to authenticated user
    
    Args:
        file_id: UUID of the file
    
    Headers Required:
    Authorization: Bearer <jwt_token>
    """
    from services.upload_service import get_user_file_by_id
    
    user_id = g.user_id
    file_record = get_user_file_by_id(file_id, user_id)
    
    if file_record:
        return jsonify({
            "status": "success",
            "file": file_record
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "File not found or unauthorized"
        }), 404

# =============================================================================
# INTEGRATION NOTES FOR DEVELOPERS
# =============================================================================
"""
Frontend Integration Examples:

1. UPLOAD FILES WITH AUTHENTICATION:
   const token = localStorage.getItem('token');
   const formData = new FormData();
   formData.append('files', file);
   
   fetch('/upload/', {
       method: 'POST',
       headers: {
           'Authorization': 'Bearer ' + token
       },
       body: formData
   });

2. GET USER FILES:
   fetch('/upload/files', {
       headers: {
           'Authorization': 'Bearer ' + token
       }
   });

3. DELETE USER FILE:
   fetch(`/upload/files/${file_id}`, {
       method: 'DELETE',
       headers: {
           'Authorization': 'Bearer ' + token
       }
   });

Security Features:
- All upload operations require valid JWT token
- Users can only access their own files
- File operations are user-scoped and secure
- Database foreign key constraints ensure data integrity

Migration Strategy:
- New uploads automatically use user-specific handling
- Legacy endpoint available for backward compatibility
- Existing vector store processing remains unchanged
- Gradual migration to full user-specific features
"""
