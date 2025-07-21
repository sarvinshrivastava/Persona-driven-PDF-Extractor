import fitz # PyMuPDF
import json
import argparse
import os

# Import the modular functions
from toc_extractor import extract_from_toc
from metadata_extractor import extract_from_metadata
from title_extractor import extract_by_prominence
from outline_extractor import extract_by_font_size
from ocr_fallback import ocr_first_page_for_title

def process_pdf(pdf_path: str):
    """
    Main execution function that runs the full extraction pipeline.
    
    Args:
        pdf_path: The path to the PDF file to process.
    """
    print(f"\n--- Starting PDF Extraction Pipeline for: {pdf_path} ---")

    try:
        # Step 1: File Setup (Load PDF)
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Critical Error: Could not open or process the PDF file. Reason: {e}")
        return

    final_title = ""
    final_outline = []

    # Step 2: Try Built-In Bookmarks (TOC) for the outline
    final_outline = extract_from_toc(doc)
    print("-" * 20)

    # --- Title Extraction Logic ---
    # Step 3: Try PDF Metadata Title
    final_title = extract_from_metadata(doc)
    print("-" * 20)

    # Step 4: Prominence-Based Title Detection (if metadata title is missing/generic)
    generic_titles = ['title', 'untitled']
    if not final_title or final_title.lower() in generic_titles:
        final_title = extract_by_prominence(doc)
    print("-" * 20)

    # --- Outline Extraction Logic ---
    # Step 5 & 6: Font-Size-Based Outline Extraction (if TOC was empty)
    if not final_outline:
        final_outline = extract_by_font_size(doc)
    print("-" * 20)

    # --- Fallback Logic ---
    # Step 7: Selective Tesseract OCR Fallback (if still no title)
    has_text_content = bool(final_title) or bool(final_outline)
    if not has_text_content:
        print("\nInfo: No text-based title or outline found. Attempting OCR as a last resort.")
        ocr_title = ocr_first_page_for_title(doc)
        if ocr_title:
            final_title = ocr_title
    print("-" * 20)
    
    # Step 8: Write Final JSON
    output_data = {
        "title": final_title,
        "outline": final_outline
    }

    print("\n--- FINAL JSON OUTPUT ---")
    print(json.dumps(output_data, indent=4))
    
    # Save to file
    output_filename = os.path.splitext(os.path.basename(pdf_path))[0] + "_output.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
    print(f"\nOutput saved to {output_filename}")

    doc.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Extracts title and outline from a PDF file based on the strategy in the provided document."
    )
    parser.add_argument("pdf_path", type=str, help="The path to the PDF file.")
    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: The file '{args.pdf_path}' does not exist.")
    else:
        process_pdf(args.pdf_path)


