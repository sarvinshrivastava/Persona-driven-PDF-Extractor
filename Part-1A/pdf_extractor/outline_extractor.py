from .utils import load_document

def extract_font_outline(path, top_n_sizes=3):
    doc = load_document(path)
    spans = []
    for page in doc:
        for block in page.get_text("dict")['blocks']:
            if block['type'] != 0:
                continue
            for line in block['lines']:
                for span in line['spans']:
                    spans.append({
                        'text': span['text'],
                        'size': span['size'],
                        'page': page.number + 1
                    })
    # cluster sizes
    sizes = sorted({s['size'] for s in spans}, reverse=True)
    levels = sizes[:top_n_sizes]
    outline = []
    level_map = {levels[0]: 'H1', levels[1] if len(levels)>1 else levels[0]: 'H2', levels[2] if len(levels)>2 else levels[1] if len(levels)>1 else levels[0]: 'H3'}
    for span in spans:
        lvl = level_map.get(span['size'])
        if lvl:
            outline.append({'level': lvl, 'text': span['text'], 'page': span['page']})
    # TODO: validate heading rules
    return outline
