# =============================================================================
# USER-SPECIFIC UPLOAD CONTROLLER
# =============================================================================
"""
Enhanced Upload Controller with User Session Management

This controller handles user-specific file uploads with authentication.
It integrates with the enhanced upload service to provide user-isolated
file management and tracking.

Features:
- Authentication-protected upload endpoints
- User-specific file organization
- Database tracking with user_id
- Backward compatibility for legacy code

Author: [Your Team]
Created for: User-Specific Sessions Implementation
"""

from flask import jsonify, g
from services.upload_service import save_uploaded_file, get_user_files
from services.folder_tree_service import build_folder_tree
from extensions import celery

def handle_upload_pdfs(request):
    """
    Handle PDF upload with user-specific session management
    
    This function:
    1. Checks if user is authenticated (g.user_id from @require_auth)
    2. Saves files to user-specific folders
    3. Records file metadata in database
    4. Returns upload results with user context
    
    Args:
        request: Flask request object containing files
    
    Returns:
        JSON response with upload status and file information
    """
    
    if 'files' not in request.files:
        return jsonify({"error": "No files found"}), 400

    files = request.files.getlist('files')
    if not files or all(file.filename == '' for file in files):
        return jsonify({"error": "No files selected"}), 400

    saved_files = []
    user_id = getattr(g, 'user_id', None)  # Get user_id from auth decorator
    
    for file_in in files:
        if file_in.filename == '':
            continue
            
        # STEP 1: Save file with user-specific handling
        if user_id:
            # User is authenticated - use user-specific upload
            file_info = save_uploaded_file(file_in, user_id)
            saved_files.append({
                'file_id': file_info['file_id'],
                'filename': file_info['filename'],
                'original_filename': file_info['original_filename'],
                'file_path': file_info['file_path'],
                'file_size': file_info['file_size'],
                'user_specific': True
            })
        else:
            # No authentication - use legacy upload (for backward compatibility)
            rel_path = save_uploaded_file(file_in)
            saved_files.append({
                'file_path': rel_path,
                'filename': file_in.filename,
                'user_specific': False
            })

    # STEP 2: Build folder tree (considering user context)
    if user_id:
        # For authenticated users, could build user-specific tree
        folder_tree = build_user_folder_tree(user_id)
    else:
        # Legacy folder tree for non-authenticated uploads
        folder_tree = build_folder_tree()

    # STEP 3: Return response with user context
    response_data = {
        "uploaded_files": saved_files,
        "folder_tree": folder_tree,
        "user_authenticated": bool(user_id),
        "total_files": len(saved_files)
    }
    
    if user_id:
        response_data["user_id"] = user_id

    return jsonify(response_data), 200

def build_user_folder_tree(user_id):
    """
    Build folder tree for authenticated user's files
    
    This function creates a user-specific folder structure
    showing only the files that belong to the authenticated user.
    
    Args:
        user_id: UUID of the authenticated user
    
    Returns:
        dict: User-specific folder tree structure
    """
    try:
        # Get user's files from database
        user_files = get_user_files(user_id)
        
        # Build tree structure from user files
        tree = {
            "name": f"user_{user_id}",
            "type": "folder",
            "children": []
        }
        
        for file_record in user_files:
            file_node = {
                "name": file_record['original_filename'],
                "type": "file",
                "file_id": file_record['id'],
                "file_path": file_record['file_path'],
                "file_size": file_record['file_size'],
                "uploaded_at": file_record['uploaded_at'],
                "upload_status": file_record['upload_status'],
                "summary_status": file_record['summary_status']
            }
            tree["children"].append(file_node)
        
        return tree
        
    except Exception as e:
        print(f"Error building user folder tree: {str(e)}")
        # Fallback to legacy folder tree
        return build_folder_tree()

def get_user_files_list(user_id):
    """
    Get list of files for authenticated user
    
    This endpoint returns only the files that belong to the
    authenticated user, providing user-specific file management.
    
    Args:
        user_id: UUID of the authenticated user
    
    Returns:
        JSON response with user's file list
    """
    try:
        user_files = get_user_files(user_id)
        
        return jsonify({
            "status": "success",
            "files": user_files,
            "total_files": len(user_files),
            "user_id": user_id
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve user files: {str(e)}"
        }), 500

def check_task_status(task_id):
    """
    Check processing task status
    
    This function remains unchanged but could be enhanced
    to include user-specific task tracking in the future.
    """
    task = celery.AsyncResult(task_id)

    if task.state == 'PENDING':
        return jsonify({"status": "pending"})

    elif task.state == 'PROGRESS':
        return jsonify({
            "status": "processing",
            "progress": task.info.get("progress", 0),
            "message": task.info.get("status", "Processing..."),
        })

    elif task.state == 'SUCCESS':
        result = task.result or {}
        return jsonify({
            "status": "completed",
            "filename": result.get("filename"),
            "summary": result.get("summary_text"),
            "summary_path": result.get("summary_path"),
            "processing_method": result.get("processing_method", "standard"),
            "chunks_processed": result.get("chunks_processed"),
            "processing_time": result.get("processing_time")
        })

    elif task.state == 'FAILURE':
        return jsonify({
            "status": "failed",
            "error": str(task.result)
        })

    else:
        return jsonify({"status": task.state.lower()})

# =============================================================================
# USAGE NOTES FOR DEVELOPERS
# =============================================================================
"""
Integration with Routes:

1. PROTECTED UPLOAD ROUTE:
   from utils.auth_utils import require_auth
   
   @upload_bp.route('/', methods=['POST'])
   @require_auth  # Add this decorator
   def upload_pdfs():
       return handle_upload_pdfs(request)

2. USER FILES LIST ROUTE:
   @upload_bp.route('/files', methods=['GET'])
   @require_auth
   def list_user_files():
       return get_user_files_list(g.user_id)

3. FRONTEND INTEGRATION:
   - Include Authorization header in upload requests
   - Handle user-specific file listings
   - Display user context in file management UI

4. BACKWARD COMPATIBILITY:
   - Non-authenticated uploads still work (legacy mode)
   - Existing vector store processing unchanged
   - Gradual migration to user-specific features
"""


def check_task_status(task_id):
    task = celery.AsyncResult(task_id)

    if task.state == 'PENDING':
        return jsonify({"status": "pending"})

    elif task.state == 'PROGRESS':
        return jsonify({
            "status": "processing",
            "progress": task.info.get("progress", 0),
            "message": task.info.get("status", "Processing..."),
        })

    elif task.state == 'SUCCESS':
        result = task.result or {}
        return jsonify({
            "status": "completed",
            "filename": result.get("filename"),
            "summary": result.get("summary_text"),
            "summary_path": result.get("summary_path"),
            "processing_method": result.get("processing_method", "standard"),
            "chunks_processed": result.get("chunks_processed"),
            "processing_time": result.get("processing_time")
        })

    elif task.state == 'FAILURE':
        return jsonify({
            "status": "failed",
            "error": str(task.result)
        })

    else:
        return jsonify({"status": task.state.lower()})
