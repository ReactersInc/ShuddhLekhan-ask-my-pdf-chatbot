# =============================================================================
# USER-SPECIFIC LIST SERVICE
# =============================================================================
"""
Enhanced List Service with User-Specific Session Management

This service provides file listing capabilities with user authentication
and user-specific filtering. It supports both database-driven user lists
and legacy filesystem-based listing for backward compatibility.

Features:
- User-specific file listing from database
- Summary integration with file records
- Legacy filesystem listing for non-authenticated access
- Hybrid approach supporting gradual migration

Author: [Your Team]
Created for: User-Specific Sessions Implementation
"""

import os
from database.supabase_admin import supabase_admin

UPLOAD_FOLDER = 'uploads'
SUMMARY_FOLDER = 'summaries'

def get_user_pdfs_with_summaries(user_id):
    """
    Get all PDFs and summaries for a specific authenticated user
    
    This function retrieves user-specific files from the database
    and includes their summary information if available.
    
    Args:
        user_id: UUID of the authenticated user
    
    Returns:
        list: User's PDF files with summary information
    """
    try:
        # STEP 1: Get user's files from database
        result = supabase_admin.table('user_files')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('file_type', 'pdf')\
            .order('uploaded_at', desc=True)\
            .execute()
        
        if not result.data:
            return []
        
        user_pdfs = []
        
        # STEP 2: Process each file and add summary information
        for file_record in result.data:
            pdf_info = {
                'file_id': file_record['id'],
                'filename': file_record['original_filename'],
                'file_path': file_record['file_path'],
                'file_size': file_record['file_size'],
                'uploaded_at': file_record['uploaded_at'],
                'upload_status': file_record['upload_status'],
                'summary_status': file_record['summary_status'],
                'summary': 'Summary not available'
            }
            
            # STEP 3: Try to load summary if available
            if file_record['summary_file_path']:
                summary_path = os.path.join(SUMMARY_FOLDER, file_record['summary_file_path'])
                summary = load_summary_file(summary_path)
                if summary:
                    pdf_info['summary'] = summary
                    pdf_info['summary_status'] = 'completed'
            else:
                # Try to find summary using legacy naming convention
                legacy_summary = find_legacy_summary(file_record['file_path'])
                if legacy_summary:
                    pdf_info['summary'] = legacy_summary
                    pdf_info['summary_status'] = 'completed (legacy)'
            
            user_pdfs.append(pdf_info)
        
        return user_pdfs
        
    except Exception as e:
        print(f"Error retrieving user PDFs: {str(e)}")
        return []

def get_all_pdf_with_summaries():
    """
    Legacy function: Get all PDFs with summaries (non-user-specific)
    
    This function maintains backward compatibility for non-authenticated
    access or during migration period. It scans the filesystem directly.
    
    Returns:
        list: All PDF files found in uploads folder with summaries
    """
    pdfs = []

    # Walk through all uploaded files recursively
    for root, _, files in os.walk(UPLOAD_FOLDER):
        for filename in files:
            if filename.endswith(".pdf"):
                # Get relative path from uploads folder
                abs_path = os.path.join(root, filename)
                relative_path = os.path.relpath(abs_path, start=UPLOAD_FOLDER)
                
                pdf_name = os.path.splitext(filename)[0]
                
                # Construct corresponding summary path
                summary_rel_path = os.path.splitext(relative_path)[0] + ".txt"
                summary_file_path = os.path.join(SUMMARY_FOLDER, summary_rel_path)

                summary = load_summary_file(summary_file_path)
                if not summary:
                    summary = "Summary not available"

                pdfs.append({
                    "filename": relative_path,
                    "summary": summary
                })

    return pdfs

def load_summary_file(summary_file_path):
    """
    Load summary content from file with multiple encoding support
    
    Args:
        summary_file_path: Path to the summary file
    
    Returns:
        str: Summary content or None if file doesn't exist/can't be read
    """
    if not os.path.exists(summary_file_path):
        return None
    
    try:
        # Try multiple encodings to handle different file formats
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                with open(summary_file_path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue  # Try next encoding
        
        # If all encodings fail, read as binary and decode with errors='ignore'
        with open(summary_file_path, "rb") as f:
            return f.read().decode('utf-8', errors='ignore')
            
    except Exception as e:
        return f"Error reading summary: {str(e)}"

def find_legacy_summary(file_path):
    """
    Find summary using legacy naming convention
    
    This function helps bridge the gap between old summary storage
    and new user-specific structure during migration.
    
    Args:
        file_path: Relative path to the PDF file
    
    Returns:
        str: Summary content or None if not found
    """
    # Construct legacy summary path
    summary_rel_path = os.path.splitext(file_path)[0] + ".txt"
    summary_file_path = os.path.join(SUMMARY_FOLDER, summary_rel_path)
    
    return load_summary_file(summary_file_path)

def update_file_summary_status(file_id, summary_file_path, status='completed'):
    """
    Update file record with summary information
    
    This function is called after summary generation to update
    the database record with summary file path and status.
    
    Args:
        file_id: UUID of the file record
        summary_file_path: Path to the generated summary file
        status: Summary processing status
    
    Returns:
        bool: True if update successful, False otherwise
    """
    try:
        result = supabase_admin.table('user_files')\
            .update({
                'summary_file_path': summary_file_path,
                'summary_status': status,
                'processed_at': 'now()'
            })\
            .eq('id', file_id)\
            .execute()
        
        return bool(result.data)
    except Exception as e:
        print(f"Error updating file summary status: {str(e)}")
        return False

def get_user_file_count(user_id):
    """
    Get total file count for a user
    
    Args:
        user_id: UUID of the user
    
    Returns:
        int: Number of files belonging to the user
    """
    try:
        result = supabase_admin.table('user_files')\
            .select('id', count='exact')\
            .eq('user_id', user_id)\
            .execute()
        
        return result.count if result.count is not None else 0
    except Exception as e:
        print(f"Error getting user file count: {str(e)}")
        return 0

# =============================================================================
# USAGE NOTES FOR DEVELOPERS
# =============================================================================
"""
How to Use the Enhanced List Service:

1. FOR AUTHENTICATED USER LISTINGS:
   from utils.auth_utils import require_auth
   from flask import g
   
   @app.route('/pdfs')
   @require_auth
   def get_user_pdfs():
       user_id = g.user_id
       pdfs = get_user_pdfs_with_summaries(user_id)
       return jsonify(pdfs)

2. FOR LEGACY COMPATIBILITY:
   # Non-authenticated listing (legacy)
   all_pdfs = get_all_pdf_with_summaries()

3. SUMMARY INTEGRATION:
   # After summary generation, update file record
   update_file_summary_status(file_id, summary_path, 'completed')

4. USER STATISTICS:
   file_count = get_user_file_count(user_id)

Data Flow:
- User uploads PDF → saved to user_files table
- Summary generated → summary_file_path updated
- User requests list → filtered by user_id
- Summary loaded and included in response

Migration Strategy:
- New code uses get_user_pdfs_with_summaries()
- Legacy code continues to use get_all_pdf_with_summaries()
- Summary files gradually linked to database records
- No breaking changes to existing functionality
"""