import fitz  # PyMuPDF
import json
from concurrent.futures import ProcessPoolExecutor

def load_document(path):
    """Load PDF document."""
    return fitz.open(path)

def write_json(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
