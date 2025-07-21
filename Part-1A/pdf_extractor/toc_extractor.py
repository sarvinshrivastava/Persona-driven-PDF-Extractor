from .utils import load_document

def extract_toc(path):
    doc = load_document(path)
    toc = doc.get_toc(simple=False)
    if toc:
        result = [{"level": f"H{item[0]}", "text": item[1], "page": item[2]} for item in toc]
        return result
    return []
