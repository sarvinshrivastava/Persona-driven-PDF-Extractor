import os
from .toc_extractor import extract_toc
from .title_extractor import extract_metadata_title, extract_prominence_title
from .outline_extractor import extract_font_outline
from .ocr_fallback import extract_ocr_title
from .utils import write_json

def process(path, output):
    data = {'title': None, 'outline': []}
    # Step 1: TOC
    toc = extract_toc(path)
    if toc:
        data['outline'] = toc
    # Title: metadata
    title = extract_metadata_title(path)
    if title:
        data['title'] = title
    else:
        # prominence
        prom = extract_prominence_title(path)
        data['title'] = prom or extract_ocr_title(path)
    # Outline fallback
    if not data['outline']:
        data['outline'] = extract_font_outline(path)
    write_json(data, output)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='PDF Title & Outline Extractor')
    parser.add_argument('input', help='input PDF file or directory')
    parser.add_argument('output', help='output JSON file or directory')
    args = parser.parse_args()

    if os.path.isdir(args.input):
        from concurrent.futures import ProcessPoolExecutor
        files = [f for f in os.listdir(args.input) if f.lower().endswith('.pdf')]
        with ProcessPoolExecutor() as ex:
            for f in files:
                inpath = os.path.join(args.input, f)
                outpath = os.path.join(args.output, f.replace('.pdf','.json'))
                ex.submit(process, inpath, outpath)
    else:
        process(args.input, args.output)
