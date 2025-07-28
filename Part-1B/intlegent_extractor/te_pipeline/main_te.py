import json
import argparse
import os

# The main logic is now imported from the new chunk_extractor module.
from chunk_extractor import parse_pdf_to_chunks

def main(pdf_path: str):
    """
    Main execution function to parse a PDF and generate content chunks.

    Args:
        pdf_path: The path to the PDF file to be processed.
    """
    if not os.path.exists(pdf_path):
        print(f"CRITICAL ERROR: The file '{pdf_path}' does not exist.")
        return

    # --- 1. Call the reusable function to do all the work ---
    chunks = parse_pdf_to_chunks(pdf_path)

    if not chunks:
        print("\n--- Pipeline finished: No content chunks were extracted. ---")
        return

    # --- 2. Save the results to a file ---
    output_filename = os.path.splitext(os.path.basename(pdf_path))[0] + "_chunks.json"
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=4)
        
        print(f"\n--- FINAL: Output saved to {output_filename} ---")
        print(f"Total chunks created: {len(chunks)}")
        # Print a summary of the first chunk for a quick preview.
        if chunks:
            print("\n--- Example First Chunk ---")
            print(json.dumps(chunks[0], indent=4))

    except Exception as e:
        print(f"CRITICAL ERROR: Could not write output to file. Reason: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Parses a PDF file, identifies sections based on headings, and extracts the content for each section into a structured JSON file."
    )
    parser.add_argument("pdf_path", type=str, help="The path to the PDF file.")
    args = parser.parse_args()

    main(args.pdf_path)

