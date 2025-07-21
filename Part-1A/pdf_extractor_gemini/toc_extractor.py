import fitz  # PyMuPDF
import json

def extract_from_toc(doc: fitz.Document):
    """
    Extracts the outline from the PDF's Table of Contents (bookmarks).
    This implements Step 2 of the pipeline.

    Args:
        doc: The PyMuPDF document object.

    Returns:
        A list of outline items if a TOC is found, otherwise an empty list.
    """
    print("Step 2: Trying to extract from built-in Table of Contents (Bookmarks)...")
    toc = doc.get_toc()

    if not toc:
        print("Info: No valid Table of Contents found in the document.")
        return []

    print(f"Success: Found a Table of Contents with {len(toc)} entries.")
    
    outline = []
    for level, title, page_num in toc:
        outline.append({
            "level": f"H{level}",
            "text": title,
            "page": page_num
        })
        
    return outline

if __name__ == '__main__':
    # Example usage:
    try:
        # Replace with a path to a PDF that has bookmarks
        pdf_path = "example.pdf" 
        document = fitz.open(pdf_path)
        outline_data = extract_from_toc(document)
        
        if outline_data:
            print("\n--- Extracted TOC Outline ---")
            print(json.dumps(outline_data, indent=4))
        
    except FileNotFoundError:
        print(f"Error: The file '{pdf_path}' was not found. Please provide a valid path for testing.")
    except Exception as e:
        print(f"An error occurred: {e}")
