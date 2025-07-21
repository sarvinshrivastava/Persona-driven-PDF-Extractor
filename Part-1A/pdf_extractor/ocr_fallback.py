import subprocess
import tempfile
from .utils import load_document

def extract_ocr_title(path, languages=['eng'], psm=6):
    doc = load_document(path)
    page = doc.load_page(0)
    pix = page.get_pixmap()
    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    pix.save(tmp.name)
    cmd = [
        'tesseract', tmp.name, 'stdout',
        '--psm', str(psm), '-l', '+'.join(languages)
    ]
    text = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8').strip()
    return text if text else None
