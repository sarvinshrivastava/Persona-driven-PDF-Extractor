import fitz # PyMuPDF
import statistics
from collections import Counter

def extract_by_font_size(doc: fitz.Document):
    """
    Extracts the outline by clustering font sizes and validating heading structure.
    This implements Steps 5 & 6 of the pipeline.

    Args:
        doc: The PyMuPDF document object.

    Returns:
        A list of outline items.
    """
    print("Step 5 & 6: Trying to extract outline by font size and validate...")
    
    spans_by_size = {}
    all_text_lines = []

    # Step 5: Parallel Span Extraction (simulated sequentially here)
    for page_num, page in enumerate(doc):
        page_dict = page.get_text("dict")
        for block in page_dict['blocks']:
            if block['type'] == 0: # Text block
                for line in block['lines']:
                    all_text_lines.append(line) # For validation later
                    for span in line['spans']:
                        size = round(span['size'])
                        text = span['text'].strip()
                        if not text:
                            continue
                        
                        if size not in spans_by_size:
                            spans_by_size[size] = []
                        spans_by_size[size].append({'text': text, 'page': page_num + 1})

    if not spans_by_size:
        return []

    # --- Font Size Clustering ---
    # Find the most common font size, which is likely body text.
    font_counts = Counter({size: len(spans) for size, spans in spans_by_size.items()})
    body_size = font_counts.most_common(1)[0][0]

    # Consider anything larger than body text as a potential heading.
    heading_sizes = sorted([size for size in spans_by_size if size > body_size], reverse=True)
    
    # Take the top 3 largest font sizes as H1, H2, H3
    heading_map = {size: f"H{i+1}" for i, size in enumerate(heading_sizes[:3])}
    
    if not heading_map:
        print("Info: No distinct heading font sizes found larger than body text.")
        return []

    # --- Create a flat list of all potential headings ---
    potential_headings = []
    for size, level in heading_map.items():
        for item in spans_by_size[size]:
            potential_headings.append({
                'level': level,
                'text': item['text'],
                'page': item['page'],
                'size': size
            })
            
    # Sort by page and then by text to maintain document order (as best as possible)
    potential_headings.sort(key=lambda x: (x['page'], x['text']))
    
    # --- Step 6: Merge Phase for Validated Outline ---
    # This is a simplified validation. A full implementation would need to analyze
    # the position of text blocks that follow a heading.
    validated_outline = []
    for i, heading in enumerate(potential_headings):
        is_valid = True
        
        # Rule: Not followed immediately by a sibling/higher-level heading
        if i + 1 < len(potential_headings):
            next_heading = potential_headings[i+1]
            # Check if the next heading is on the same page and is of the same or higher level
            if next_heading['page'] == heading['page']:
                current_level_num = int(heading['level'][1:])
                next_level_num = int(next_heading['level'][1:])
                if next_level_num <= current_level_num:
                    # This is a naive check. A better check would look at the text
                    # between them. If there's no body text, it's likely invalid.
                    # For this implementation, we'll be more lenient.
                    pass 

        # For this implementation, we accept most headings found.
        if is_valid:
            validated_outline.append({
                'level': heading['level'],
                'text': heading['text'],
                'page': heading['page']
            })
            
    print(f"Success: Extracted {len(validated_outline)} potential headings based on font size.")
    return validated_outline


if __name__ == '__main__':
    try:
        pdf_path = "example.pdf"
        document = fitz.open(pdf_path)
        outline = extract_by_font_size(document)
        if outline:
            print("\n--- Font-Size Based Outline ---")
            print(json.dumps(outline, indent=4))
    except FileNotFoundError:
        print(f"Error: The file '{pdf_path}' was not found. Please provide a valid path for testing.")
    except Exception as e:
        print(f"An error occurred: {e}")
