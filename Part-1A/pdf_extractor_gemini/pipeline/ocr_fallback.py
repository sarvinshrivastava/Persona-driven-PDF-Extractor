import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io

# --- Configuration for Tesseract ---
# If tesseract is not in your PATH, include the following line:
# pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'
# For example, on Windows:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ocr_first_page_for_title(doc: fitz.Document):
    """
    Performs OCR on the first page as a fallback for title extraction.
    This implements Step 7 of the pipeline.

    Args:
        doc: The PyMuPDF document object.

    Returns:
        The OCR'd text, or an empty string if it fails.
    """
    print("Step 7: Trying OCR fallback for title on the first page...")
    if doc.page_count == 0:
        return ""

    try:
        first_page = doc[0]
        
        # Check if the page has any text. If it does, OCR is likely not needed.
        if first_page.get_text():
            print("Info: Page already contains text. Skipping OCR.")
            return ""

        # Render page to an image (pixmap)
        pix = first_page.get_pixmap(dpi=300)
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))

        # Use Tesseract to do OCR on the image
        # --psm 6: Assume a single uniform block of text.
        # -l eng+hin+jpn: Languages to use for OCR
        custom_config = r'--psm 6 -l eng+hin+jpn'
        text = pytesseract.image_to_string(image, config=custom_config)
        
        cleaned_text = text.strip().replace('\n', ' ').replace('  ', ' ')

        if cleaned_text:
            print(f"Success: Found text via OCR: '{cleaned_text}'")
        else:
            print("Info: OCR did not yield any text.")
            
        return cleaned_text

    except pytesseract.TesseractNotFoundError:
        print("\n--- TESSERACT ERROR ---")
        print("Error: `tesseract` is not installed or not in your PATH.")
        print("Please install Tesseract OCR engine and configure the path in `ocr_fallback.py` if needed.")
        print("-----------------------\n")
        return ""
    except Exception as e:
        print(f"An error occurred during OCR: {e}")
        return ""

if __name__ == '__main__':
    try:
        # Replace with a path to a scanned (image-only) PDF
        pdf_path = "scanned_example.pdf" 
        document = fitz.open(pdf_path)
        title = ocr_first_page_for_title(document)
        if title:
            print(f"\nOCR'd Title: {title}")
    except FileNotFoundError:
        print(f"Error: The file '{pdf_path}' was not found. Create a scanned PDF for testing.")
    except Exception as e:
        print(f"An error occurred: {e}")

