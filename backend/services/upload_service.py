# =============================================================================
# USER-SPECIFIC UPLOAD SERVICE
# =============================================================================
"""
Enhanced Upload Service with User-Specific Session Management

This service implements the Hybrid Approach for user-specific file management:
1. Database-Level Filtering: All uploads linked to user_id
2. File System Separation: User-specific folders (uploads/user_123/)
3. Metadata Tracking: Complete file info stored in user_files table

Features:
- User-specific file storage and organization
- Database tracking with user_id foreign keys
- Secure file paths and folder structure
- Integration with existing vector store processing

Author: [Your Team]
Created for: User-Specific Sessions Implementation
"""

import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from database.supabase_admin import supabase_admin

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_uploaded_file(file, user_id=None):
    """
    Save uploaded file with user-specific database tracking and folder structure preservation
    
    Files are stored with their original folder structure preserved but tracked by user_id in database.
    Each user only sees their own files through database filtering.
    
    Args:
        file: Uploaded file object from Flask request
        user_id: UUID of authenticated user (optional for backward compatibility)
    
    Returns:
        dict: File information or string path for legacy compatibility
    """
    if not file or file.filename == '':
        raise ValueError("No file provided")
    
    # STEP 1: Process and secure filename, preserving folder structure
    original_filename = file.filename
    
    # Handle folder uploads - preserve the folder structure
    if '/' in original_filename:
        # Split path and secure each component
        path_components = original_filename.split('/')
        sanitized_components = [secure_filename(part) for part in path_components if part]  # Remove empty parts
        safe_relative_path = os.path.join(*sanitized_components)
        
        # Extract just the filename for unique naming
        original_file_name = sanitized_components[-1]
        folder_path = os.path.join(*sanitized_components[:-1]) if len(sanitized_components) > 1 else ""
    else:
        # Single file upload
        safe_relative_path = secure_filename(original_filename)
        original_file_name = safe_relative_path
        folder_path = ""
    
    # STEP 2: Generate unique filename to prevent conflicts
    name, ext = os.path.splitext(original_file_name)
    unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
    
    # STEP 3: Build full path preserving folder structure
    if folder_path:
        final_relative_path = os.path.join(folder_path, unique_filename)
        full_upload_path = os.path.join(UPLOAD_FOLDER, folder_path)
    else:
        final_relative_path = unique_filename
        full_upload_path = UPLOAD_FOLDER
    
    # STEP 4: Create directory structure if needed
    os.makedirs(full_upload_path, exist_ok=True)
    
    # STEP 5: Save the file
    absolute_path = os.path.join(UPLOAD_FOLDER, final_relative_path)
    file.save(absolute_path)
    file_size = os.path.getsize(absolute_path)
    
    if user_id:
        # STEP 6: Save metadata to database for user-specific tracking
        try:
            file_record = {
                'user_id': user_id,
                'filename': unique_filename,
                'original_filename': original_file_name,  # Just the filename
                'file_path': final_relative_path,  # Full relative path with folders (will extract folder from this)
                'file_size': file_size,
                'file_type': 'pdf',
                'upload_status': 'completed',
                'summary_status': 'pending',
                'uploaded_at': datetime.utcnow().isoformat()
            }
            
            # Insert file record into user_files table
            result = supabase_admin.table('user_files').insert(file_record).execute()
            
            if result.data:
                file_id = result.data[0]['id']
                # Return structured info for user-specific uploads
                return {
                    'file_id': file_id,
                    'filename': unique_filename,
                    'original_filename': original_file_name,
                    'folder_path': folder_path,  # Include folder info for frontend
                    'file_path': final_relative_path,
                    'absolute_path': absolute_path,
                    'relative_path': final_relative_path,  # For legacy compatibility
                    'file_size': file_size,
                    'user_id': user_id
                }
            else:
                # If database insert fails, remove the file
                if os.path.exists(absolute_path):
                    os.remove(absolute_path)
                raise Exception("Failed to save file metadata to database")
                
        except Exception as e:
            # If database operation fails, remove the file
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
            raise Exception(f"Error saving file metadata: {str(e)}")
    
    else:
        # STEP 7: Legacy upload (no user tracking) - just return filename
        return final_relative_path

def _save_file_legacy(file):
    """
    Legacy file saving function for backward compatibility
    
    This maintains the old behavior when user_id is not provided.
    Used for non-authenticated endpoints or migration period.
    """
    original_relative_path = file.filename
    path_components = original_relative_path.split('/')
    sanitized_components = [secure_filename(part) for part in path_components]
    safe_relative_path = os.path.join(*sanitized_components)

    # Saving the Uploaded files or Folders in the UPLOAD Directory
    absolute_save_path = os.path.join(UPLOAD_FOLDER, safe_relative_path)
    os.makedirs(os.path.dirname(absolute_save_path), exist_ok=True)
    file.save(absolute_save_path)

    return safe_relative_path

def get_user_files(user_id):
    """
    Retrieve all files for a specific user
    
    Args:
        user_id: UUID of the user
    
    Returns:
        list: User's file records from database
    """
    try:
        result = supabase_admin.table('user_files')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('uploaded_at', desc=True)\
            .execute()
        
        return result.data if result.data else []
    except Exception as e:
        print(f"Error retrieving user files: {str(e)}")
        return []

def get_user_file_by_id(file_id, user_id):
    """
    Get specific file by ID, ensuring it belongs to the user
    
    Args:
        file_id: UUID of the file
        user_id: UUID of the user (for security check)
    
    Returns:
        dict: File record or None if not found/unauthorized
    """
    try:
        result = supabase_admin.table('user_files')\
            .select('*')\
            .eq('id', file_id)\
            .eq('user_id', user_id)\
            .execute()
        
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error retrieving file: {str(e)}")
        return None

def delete_user_file(file_id, user_id):
    """
    Delete file from both filesystem and database
    
    Args:
        file_id: UUID of the file to delete
        user_id: UUID of the user (for security check)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # STEP 1: Get file record to ensure user owns it
        file_record = get_user_file_by_id(file_id, user_id)
        if not file_record:
            return False
        
        # STEP 2: Delete physical file
        file_path = os.path.join(UPLOAD_FOLDER, file_record['file_path'])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # STEP 3: Delete database record
        result = supabase_admin.table('user_files')\
            .delete()\
            .eq('id', file_id)\
            .eq('user_id', user_id)\
            .execute()
        
        return True
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        return False

# =============================================================================
# MIGRATION AND COMPATIBILITY FUNCTIONS
# =============================================================================

def get_file_absolute_path(file_path):
    """
    Convert relative file path to absolute path
    
    This function maintains compatibility with existing code that expects
    absolute paths for vector store processing and other operations.
    
    Args:
        file_path: Relative path from database or legacy function
    
    Returns:
        str: Absolute path to the file
    """
    return os.path.join(UPLOAD_FOLDER, file_path)

# =============================================================================
# USAGE NOTES FOR DEVELOPERS
# =============================================================================
"""
How to Use the Enhanced Upload Service:

1. FOR NEW USER-SPECIFIC UPLOADS:
   from utils.auth_utils import require_auth
   from flask import g
   
   @app.route('/upload')
   @require_auth
   def upload():
       user_id = g.user_id
       file_info = save_uploaded_file(file, user_id)
       # file_info contains all metadata and paths

2. FOR GETTING USER FILES:
   user_files = get_user_files(user_id)
   for file in user_files:
       absolute_path = get_file_absolute_path(file['file_path'])
       # Use absolute_path for vector store processing

3. FOR LEGACY COMPATIBILITY:
   # Old code will still work during migration
   relative_path = save_uploaded_file(file)  # Without user_id
   
4. FILE ORGANIZATION:
   uploads/
   ├── user_123/
   │   ├── document_abc123.pdf
   │   └── report_def456.pdf
   └── user_456/
       └── thesis_ghi789.pdf

5. DATABASE TRACKING:
   - All files linked to user_id
   - Complete metadata stored
   - Easy to query user-specific files
   - Support for file status tracking

Migration Strategy:
- New uploads: Use save_uploaded_file(file, user_id)
- Existing vector store code: Use get_file_absolute_path()
- No breaking changes to current processing pipeline
"""
