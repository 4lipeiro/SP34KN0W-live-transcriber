import os
import json

def ensure_dir_exists(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def load_json_file(filepath, default=None):
    """Load a JSON file, return default if file doesn't exist"""
    if not os.path.exists(filepath):
        return default or {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {filepath}: {str(e)}")
        return default or {}

def save_json_file(filepath, data):
    """Save data to a JSON file"""
    directory = os.path.dirname(filepath)
    ensure_dir_exists(directory)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)