from flask import jsonify
from services.folder_tree_service import build_folder_tree
from services.folder_tree_service import get_all_uploaded_files
from services.folder_tree_service import get_all_uploaded_files, build_folder_tree, get_pdf_file

def get_document_tree():
    tree = build_folder_tree()
    return jsonify(tree)

def list_uploaded_files():
    files = get_all_uploaded_files()
    return jsonify(files)

def view_pdf_file(relative_path):
    return get_pdf_file(relative_path)  