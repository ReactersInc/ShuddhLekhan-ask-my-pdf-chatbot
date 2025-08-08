import os 

VECTOR_STORE_ROOT = "vector_store"

def find_closest_match(name:str , candidates: list[str]) -> str | None:
    
    name_lower = name.lower()

    #Exact Match 
    for c in candidates:
        if os.path.basename(c).lower() == name_lower:
            return c
        
    #Partial Match
    for c in candidates:
        if name_lower in os.path.basename(c).lower():
            return c
        
    return None



def resolve_file_path(state: dict)->dict:
    
    file_name = state.get("parameters", {}).get("file_name", "")
    
    if not file_name:
        return {**state, "error": "Missing file_name in parameters"}
    
    file_paths = []
    for root , dirs , files in os.walk(VECTOR_STORE_ROOT):
        for d in dirs:
            full_path = os.path.join(root , d)
            if os.path.exists(os.path.join(full_path, "index.faiss")):
                file_paths.append(os.path.relpath(full_path, VECTOR_STORE_ROOT))

    
    matched = find_closest_match(file_name, file_paths)

    if matched:
        state["parameters"]["file_path"] = matched
        state["resolved_file_path"] = matched
    else:
        state["error"] = f"No matching file found for '{file_name}'"

    return state

def resolve_folder_path(state: dict) -> dict:
    folder_name = state.get("parameters", {}).get("folder_name", "")
    if not folder_name:
        return {**state, "error": "Missing folder_name in parameters"}

    folder_paths = []
    for root, dirs, _ in os.walk(VECTOR_STORE_ROOT):
        for d in dirs:
            full_path = os.path.join(root, d)
            if os.path.isdir(full_path):
                folder_paths.append(os.path.relpath(full_path, VECTOR_STORE_ROOT))

    matched = find_closest_match(folder_name, folder_paths)

    if matched:
        state["parameters"]["folder_path"] = matched
        state["resolved_folder_path"] = matched
    else:
        state["error"] = f"No matching folder found for '{folder_name}'"

    return state