import fitz  # PyMuPDF
import os
import re

# Importing necessary functions from your existing modules
from toc_extractor import extract_from_toc
from outline_extractor import extract_outline as extract_outline_by_rules
from utils import detect_repeating_headers_footers, stitch_text_lines
from title_extractor import extract_title as extract_title_by_prominence

def parse_pdf_to_chunks(pdf_path: str) -> list[dict]:
    """
    Parses a PDF, extracts its outline, and divides the content into chunks
    based on the document's headings.

    This function serves as the main engine for processing a PDF file and
    returning structured, content-rich data.

    Args:
        pdf_path: The file path to the PDF document.

    Returns:
        A list of dictionaries, where each dictionary represents a chunk of content
        under a specific heading. Returns an empty list if the PDF cannot be
        processed or contains no extractable text.
    """
    print(f"--- Opening and analyzing {os.path.basename(pdf_path)} ---")
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"CRITICAL ERROR: Could not open or process the PDF file. Reason: {e}")
        return []

    # --- Step 1: Extract a clean, ordered list of headings (the outline) ---
    print("Step 1: Extracting document outline...")
    
    # First, try the most reliable method: machine-readable Table of Contents (bookmarks).
    outline = extract_from_toc(doc)

    # If no machine-readable ToC is found, fall back to visual/rule-based extraction.
    if not outline:
        print("Info: No machine-readable ToC found. Using visual rule-based extraction.")
        ignored_bboxes = detect_repeating_headers_footers(doc)
        # A prominent title helps the rules-based extractor ignore it as a heading.
        prominent_title = extract_title_by_prominence(doc, ignored_bboxes)
        outline = extract_outline_by_rules(doc, ignored_bboxes, prominent_title)

    # If still no outline, the document may not have a clear structure.
    if not outline:
        print("Warning: No outline could be extracted. Returning the whole document as a single chunk.")
        full_text = "".join(page.get_text() for page in doc)
        doc.close()
        if not full_text.strip():
            return []
        return [{
            "section_title": "Full Document",
            "page_number": 1,
            "content": full_text.strip(),
            "source_document": os.path.basename(pdf_path)
        }]

    # --- Step 2: Process the outline to extract content for each section ---
    print(f"Step 2: Processing {len(outline)} sections to create chunks...")
    
    # Ensure the outline is sorted by page number for correct processing.
    outline.sort(key=lambda x: x['page'])

    chunks = []
    # Pre-load all page text to avoid repeated calls inside the loop.
    doc_text_pages = [page.get_text() for page in doc]

    for i, section in enumerate(outline):
        section_title = section['text']
        start_page_num = section['page']  # This is 1-based

        # Determine the page range for the current section's content.
        # It ends right before the next section starts or at the end of the document.
        if i + 1 < len(outline):
            end_page_num = outline[i+1]['page']
            next_section_title = outline[i+1]['text']
        else:
            end_page_num = doc.page_count
            next_section_title = None

        # Extract the text content for the chunk.
        content = ""
        start_page_idx = start_page_num - 1
        end_page_idx = end_page_num - 1

        if start_page_idx < 0 or start_page_idx >= len(doc_text_pages):
            continue # Skip if page number is out of bounds

        try:
            if start_page_idx == end_page_idx:
                # Section starts and ends on the same page.
                page_text = doc_text_pages[start_page_idx]
                if next_section_title:
                    # Isolate text between the current and next heading.
                    content = page_text.split(section_title, 1)[-1].split(next_section_title, 1)[0]
                else:
                    # It's the last section, so take all text after the heading.
                    content = page_text.split(section_title, 1)[-1]
            else:
                # Section spans multiple pages.
                # 1. Get content from the start page (everything after the heading).
                content += doc_text_pages[start_page_idx].split(section_title, 1)[-1]

                # 2. Get content from all full pages in between.
                for page_idx in range(start_page_idx + 1, end_page_idx):
                    content += "\n\n" + doc_text_pages[page_idx]

                # 3. Get content from the end page (everything before the next heading).
                if next_section_title:
                    content += "\n\n" + doc_text_pages[end_page_idx].split(next_section_title, 1)[0]
                else: # If it's the last section in the doc
                    content += "\n\n" + doc_text_pages[end_page_idx]

        except (IndexError, ValueError):
            # Fallback in case a title isn't found in the raw text (e.g., it's an image).
            # In this case, we just concatenate the page text.
            content = ""
            for page_idx in range(start_page_idx, end_page_idx + 1):
                 if page_idx < len(doc_text_pages):
                    content += "\n\n" + doc_text_pages[page_idx]


        chunks.append({
            "section_title": section_title.strip(),
            "page_number": start_page_num,
            "content": content.strip(),
            "source_document": os.path.basename(pdf_path)
        })

    print("Step 3: Successfully created chunks.")
    doc.close()
    return chunks

