import fitz  # PyMuPDF
import json
import argparse
import os

# Importing modules
from utils import detect_repeating_headers_footers
from classifier import classify_document
from toc_extractor import extract_from_toc
from metadata_extractor import extract_from_metadata
from title_extractor import extract_title as extract_title_by_prominence
from outline_extractor import extract_outline as extract_outline_by_rules


def process_pdf(pdf_path: str):
    """Main execution function that runs the full, intelligent extraction pipeline."""
    print(f"\n--- Starting PDF Extraction Pipeline for: {pdf_path} ---")

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"CRITICAL ERROR: Could not open or process the PDF file. Reason: {e}")
        return

    # --- Phase 1: Pre-computation and Classification ---
    print("\n--- Phase 1: Pre-computation & Classification ---")
    # *** Use the new, intelligent classifier ***
    doc_type = classify_document(doc) 
    ignored_bboxes = detect_repeating_headers_footers(doc)
    
    final_title = ""
    final_outline = []

    # --- Phase 2: Adaptive Extraction ---
    print("\n--- Phase 2: Adaptive Extraction ---")

    # 1. Get machine-readable bookmarks first, as they are the most reliable source.
    print("Step 2: Checking for machine-readable bookmarks (TOC)...")
    final_outline = extract_from_toc(doc)

    # 2. Extract title using prominence. This is useful for all document types.
    print("-" * 20)
    prominent_title = extract_title_by_prominence(doc, ignored_bboxes)
    
    # 3. If no outline was found via bookmarks, use the visual/rule-based methods.
    if not final_outline:
        print("Info: No bookmarks found. Proceeding with visual outline extraction.")
        final_outline = extract_outline_by_rules(doc, ignored_bboxes, prominent_title)

    # 4. Decide on the final title based on document type
    if doc_type == "Regular":
        final_title = prominent_title
        # Fallback to metadata only if prominence fails completely
        if not final_title:
            print("Step 3: Prominence title failed, checking metadata...")
            final_title = extract_from_metadata(doc)
    else: # For Flyers, we start with an empty title
        final_title = ""

    # --- Phase 3: Post-Processing and Cleanup ---
    print("\n--- Phase 3: Post-Processing & Cleanup ---")
    
    # Rule 1: If we have a flyer with no title and a single H1, that H1 is probably the title.
    if doc_type == "Flyer" and not final_title and len(final_outline) == 1:
        print("Info: Post-processing found a single heading in a flyer. Promoting to title.")
        final_title = final_outline.pop(0)['text']
    
    # Rule 2: If the prominent title is the same as the first heading, remove the heading.
    if final_outline and prominent_title and (final_outline[0]['text'].lower().strip() == prominent_title.lower().strip()):
        print("Info: Post-processing is removing title from outline to prevent duplication.")
        final_outline.pop(0)

    output_data = {
        "title": final_title.strip(),
        "outline": final_outline
    }

    print("\n--- FINAL JSON OUTPUT ---")
    print(json.dumps(output_data, indent=4))
    
    # Save to file
    output_filename = os.path.splitext(os.path.basename(pdf_path))[0] + ".json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
    print(f"\nOutput saved to {output_filename}")

    doc.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extracts title and outline from a PDF file using an intelligent, adaptive pipeline.")
    parser.add_argument("pdf_path", type=str, help="The path to the PDF file.")
    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: The file '{args.pdf_path}' does not exist.")
    else:
        process_pdf(args.pdf_path)
