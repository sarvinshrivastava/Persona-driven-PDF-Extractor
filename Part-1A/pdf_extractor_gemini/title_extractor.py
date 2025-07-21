import fitz  # PyMuPDF

def extract_by_prominence(doc: fitz.Document):
    """
    Detects the document title using prominence-based heuristics on the first page.
    This implements Step 4 of the pipeline.

    Args:
        doc: The PyMuPDF document object.

    Returns:
        The text of the most prominent block, or an empty string.
    """
    print("Step 4: Trying to extract title by prominence (heuristic)...")
    if doc.page_count == 0:
        return ""

    first_page = doc[0]
    blocks = first_page.get_text("blocks")
    
    # Filter out small blocks and potential headers/footers
    page_height = first_page.rect.height
    page_width = first_page.rect.width
    
    potential_titles = []
    
    for block in blocks:
        # block format: (x0, y0, x1, y1, "text", block_no, block_type)
        x0, y0, x1, y1, text, _, _ = block
        
        # --- Filters from PDF ---
        # 1. Remove headers/footers (e.g., top 10% or bottom 10% of the page)
        if y0 < page_height * 0.1 or y1 > page_height * 0.9:
            continue
            
        # 2. Ignore blocks without reasonable width coverage (e.g., less than 50% of page width)
        block_width = x1 - x0
        if block_width < page_width * 0.4:
            continue
            
        # 3. Exclude URLs or watermarks (simple check)
        if 'http' in text or 'www' in text:
            continue

        # --- Calculate Prominence Score ---
        # To get avg_font_size, we need to look at the spans within the block
        block_text_for_spans = first_page.get_text("dict", clip=fitz.Rect(x0, y0, x1, y1))
        total_font_size = 0
        span_count = 0
        for block_dict in block_text_for_spans['blocks']:
            for line in block_dict['lines']:
                for span in line['spans']:
                    total_font_size += span['size']
                    span_count += 1
        
        avg_font_size = total_font_size / span_count if span_count > 0 else 0
        
        block_height = y1 - y0
        
        # prominence = avg_font_size x block_width x block_height
        prominence = avg_font_size * block_width * block_height
        potential_titles.append((prominence, text.strip()))

    if not potential_titles:
        print("Info: Could not determine title by prominence.")
        return ""

    # Select top-scoring block
    potential_titles.sort(key=lambda x: x[0], reverse=True)
    best_title = potential_titles[0][1]
    
    print(f"Success: Found potential title by prominence: '{best_title}'")
    return best_title


if __name__ == '__main__':
    try:
        pdf_path = "example.pdf"
        document = fitz.open(pdf_path)
        title = extract_by_prominence(document)
        if title:
            print(f"\nProminent Title: {title}")
    except FileNotFoundError:
        print(f"Error: The file '{pdf_path}' was not found. Please provide a valid path for testing.")
    except Exception as e:
        print(f"An error occurred: {e}")
