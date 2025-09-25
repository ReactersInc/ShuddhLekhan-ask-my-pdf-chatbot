from flask import jsonify, g, request
from services.folder_tree_service import build_folder_tree, get_all_uploaded_files, get_pdf_file
from services.upload_service import get_user_files
from services.list_service import get_user_pdfs_with_summaries

def get_document_tree():
    """
    Get user-specific document tree with folder structure preserved
    Uses authenticated user's ID to filter files from database and builds folder tree
    """
    user_id = getattr(g, 'user_id', None)
    
    if user_id:
        # Get user-specific files from database
        user_files = get_user_files(user_id)
        
        # Build folder tree structure
        folder_tree = build_user_folder_tree_from_files(user_files)
        
        return jsonify(folder_tree)
    else:
        # Fallback to legacy behavior
        tree = build_folder_tree()
        return jsonify(tree)

def build_user_folder_tree_from_files(user_files):
    """
    Build hierarchical folder tree from user's files
    Extracts folder structure from file_path field
    
    Args:
        user_files: List of user file records from database
    
    Returns:
        list: Hierarchical folder structure with files
    """
    if not user_files:
        return []
    
    # Group files by folder
    folders = {}
    root_files = []
    
    for file_record in user_files:
        file_path = file_record.get('file_path', '')
        original_filename = file_record.get('original_filename', file_record.get('filename', ''))
        
        # Extract folder from file_path (e.g., "test_ses/file.pdf" -> "test_ses")
        if '/' in file_path:
            folder_name = file_path.split('/')[0]
        elif '\\' in file_path:
            folder_name = file_path.split('\\')[0]
        else:
            folder_name = None  # File is in root
        
        if folder_name and folder_name != file_path:  # File is in a folder
            # Create folder if doesn't exist
            if folder_name not in folders:
                folders[folder_name] = {
                    "id": f"folder_{folder_name}",
                    "name": folder_name,
                    "type": "folder",
                    "children": [],
                    "isExpanded": False,
                    "count": 0
                }
            
            # Add file to folder
            file_node = {
                "id": file_record['id'],
                "name": original_filename,
                "type": "file",
                "file_id": file_record['id'],
                "file_path": file_record['file_path'],
                "file_size": file_record['file_size'],
                "uploaded_at": file_record['uploaded_at']
            }
            folders[folder_name]["children"].append(file_node)
            folders[folder_name]["count"] += 1
            
        else:  # File is in root directory
            file_node = {
                "id": file_record['id'],
                "name": original_filename,
                "type": "file",
                "file_id": file_record['id'],
                "file_path": file_record['file_path'],
                "file_size": file_record['file_size'],
                "uploaded_at": file_record['uploaded_at']
            }
            root_files.append(file_node)
    
    # Build final tree structure: folders first, then root files
    tree = list(folders.values()) + root_files
    return tree

def list_uploaded_files():
    """
    List user-specific uploaded files, optionally filtered by folder
    Uses authenticated user's ID to filter files
    """
    user_id = getattr(g, 'user_id', None)
    folder_filter = request.args.get('folder')  # Get folder parameter from query string
    
    print(f"list_uploaded_files called - user_id: {user_id}, folder_filter: {folder_filter}")
    
    if user_id:
        # Get user-specific files from database
        files = get_user_files(user_id)
        
        if not files:
            return jsonify({
                'status': 'success',
                'files': [],
                'total_files': 0,
                'user_id': user_id,
                'user_specific': True,
                'folder': folder_filter
            })
        
        # Filter by folder if specified
        if folder_filter:
            print(f"Filtering files by folder: {folder_filter}")
            filtered_files = []
            for file_record in files:
                file_path = file_record.get('file_path', '')
                print(f"Checking file: {file_path}")
                # Extract folder from file path (handle both / and \ separators)
                if '/' in file_path:
                    file_folder = file_path.split('/')[0]
                elif '\\' in file_path:
                    file_folder = file_path.split('\\')[0]
                else:
                    file_folder = None
                    
                print(f"File folder: {file_folder}, matches filter: {file_folder == folder_filter}")
                if file_folder == folder_filter:
                    filtered_files.append(file_record)
                # If no folder in path and looking for root files  
                elif folder_filter == 'root' and '/' not in file_path and '\\' not in file_path:
                    filtered_files.append(file_record)
            files = filtered_files
            print(f"Filtered results: {len(files)} files")
        
        return jsonify({
            'status': 'success',
            'pdfs': files,  # Use 'pdfs' to match frontend expectation
            'files': files,  # Keep 'files' for backward compatibility
            'total_files': len(files),
            'user_id': user_id,
            'user_specific': True,
            'folder': folder_filter
        })
    else:
        # Fallback to legacy behavior
        files = get_all_uploaded_files()
        return jsonify({
            'status': 'success',
            'pdfs': files,  # Use 'pdfs' to match frontend expectation
            'files': files,  # Keep 'files' for backward compatibility
            'total_files': len(files),
            'user_specific': False,
            'folder': folder_filter
        })

def view_pdf_file(relative_path):
    """
    View PDF file (with user security check and file type validation)
    """
    user_id = getattr(g, 'user_id', None)
    print(f"view_pdf_file called - user_id: {user_id}, relative_path: {relative_path}")
    
    # Check file extension first
    if not relative_path.lower().endswith('.pdf'):
        return jsonify({"error": "File is not a PDF document"}), 400
    
    if user_id:
        # Check if the file belongs to the user
        user_files = get_user_files(user_id)
        user_file_paths = [f['file_path'] for f in user_files]
        print(f"User file paths: {user_file_paths}")
        print(f"Looking for path: {relative_path}")
        
        # Check if the relative_path matches any user file path
        # Handle both exact matches and normalized path separators
        path_found = False
        
        for file_path in user_file_paths:
            # Normalize both paths for comparison (handle / and \ separators)
            normalized_file_path = file_path.replace('\\', '/').replace('//', '/')
            normalized_relative_path = relative_path.replace('\\', '/').replace('//', '/')
            
            print(f"Comparing: '{normalized_file_path}' with '{normalized_relative_path}'")
            
            if normalized_file_path == normalized_relative_path:
                path_found = True
                print(f"Match found!")
                break
        
        print(f"Path found: {path_found}")
        
        if not path_found:
            print(f"Access denied - file not found in user's files")
            return jsonify({"error": "Unauthorized access to file"}), 403
    
    # If authorized or legacy mode, serve the file
    print(f"Serving file: {relative_path}")
    return get_pdf_file(relative_path)  