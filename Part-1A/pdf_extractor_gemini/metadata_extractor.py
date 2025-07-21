import fitz  # PyMuPDF
import json

def extract_from_metadata(doc: fitz.Document):
    """
    Extracts the title from the PDF's metadata.
    This implements Step 3 of the pipeline.

    Args:
        doc: The PyMuPDF document object.

    Returns:
        The title string if found, otherwise an empty string.
    """
    print("Step 3: Trying to extract title from metadata...")
    
    title = doc.metadata.get('title', '')

    if title:
        print(f"Success: Found metadata title: '{title}'")
    else:
        print("Info: No title found in metadata.")
        
    return title

if __name__ == '__main__':
    # Example usage:
    try:
        # Replace with a path to a PDF that has a metadata title
        pdf_path = "example.pdf" 
        document = fitz.open(pdf_path)
        title_data = extract_from_metadata(document)
        
        if title_data:
            print(f"\nExtracted Title: {title_data}")

    except FileNotFoundError:
        print(f"Error: The file '{pdf_path}' was not found. Please provide a valid path for testing.")
    except Exception as e:
        print(f"An error occurred: {e}")
