import fitz  # PyMuPDF
from collections import Counter
import re

def stitch_text_lines(page: fitz.Page):
    """
    Robustly stitches text spans into coherent lines by respecting the block and line
    structure provided by PyMuPDF. This prevents text fragmentation.

    Args:
        page: The fitz.Page object to process.

    Returns:
        A list of dictionaries, where each dictionary represents a line of text
        with its content, bounding box, and style properties.
    """
    lines = []
    # The "dict" method provides a structured breakdown of the page content
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        if b['type'] == 0:  # This is a text block
            for l in b["lines"]:
                # Join spans within the same line
                line_text = "".join(s["text"] for s in l["spans"]).strip()
                if not line_text:
                    continue

                # Capture rich style information for the entire line
                bbox = fitz.Rect(l['bbox'])
                font_sizes = [s["size"] for s in l["spans"]]
                avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 0
                is_bold = any('bold' in s['font'].lower() for s in l['spans'])
                
                # Check for centered text
                page_width = page.rect.width
                center_x = (bbox.x0 + bbox.x1) / 2
                is_centered = abs(center_x - page_width / 2) < (page_width * 0.1) # Within 10% of center

                lines.append({
                    "text": line_text,
                    "bbox": bbox,
                    "size": avg_font_size,
                    "bold": is_bold,
                    "centered": is_centered,
                })
    return lines


def detect_repeating_headers_footers(doc: fitz.Document, sample_pages=5):
    """
    Detects repeating text elements that are likely headers or footers.
    """
    if doc.page_count <= 3:
        return []

    num_pages_to_check = min(sample_pages, doc.page_count)
    
    # Get lines from a sample of pages
    page_lines = {}
    for i in range(num_pages_to_check):
        page = doc[i]
        page_lines[i] = stitch_text_lines(page)

    # Find text that appears frequently across the sampled pages
    all_text = [line['text'].strip() for lines in page_lines.values() for line in lines if line['text'].strip()]
    text_counts = Counter(all_text)
    
    # Consider text a header/footer if it appears on more than half the sampled pages
    common_texts = {text for text, count in text_counts.items() if count > num_pages_to_check / 2}
    
    ignored_bboxes = []
    for text in common_texts:
        # Ignore purely numeric text which could be page numbers
        if not re.search(r'[a-zA-Z]', text):
            continue
            
        for lines in page_lines.values():
            for line in lines:
                if line['text'].strip() == text:
                    ignored_bboxes.append(line['bbox'])
    
    if ignored_bboxes:
        print(f"Info: Detected {len(set(common_texts))} potential header/footer text(s) to ignore.")

    return ignored_bboxes

