from .utils import load_document

def extract_metadata_title(path):
    doc = load_document(path)
    title = doc.metadata.get('title', '').strip()
    return title if title else None

def extract_prominence_title(path, filter_fn=None):
    doc = load_document(path)
    page = doc.load_page(0)
    blocks = page.get_text("blocks")
    # compute prominence score
    scored = []
    for x0, y0, x1, y1, text, block_no in blocks:
        width = x1 - x0
        height = y1 - y0
        # estimate avg font size: approximate by height / number of lines
        lines = text.count("\n") + 1
        font_size = height / lines
        score = font_size * width * height
        if filter_fn and not filter_fn((x0, y0, x1, y1, text)):
            continue
        scored.append((score, text.strip()))
    if not scored:
        return None
    # pick top
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]
