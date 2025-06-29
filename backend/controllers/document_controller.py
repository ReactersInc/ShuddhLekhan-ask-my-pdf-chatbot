from flask import jsonify
from services.folder_tree_service import build_folder_tree
from services.folder_tree_service import get_all_uploaded_files

def get_document_tree():
    tree = build_folder_tree()
    return jsonify(tree)

def list_uploaded_files():
    files = get_all_uploaded_files()
    return jsonify(files)
