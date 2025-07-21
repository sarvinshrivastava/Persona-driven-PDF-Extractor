#!/bin/bash

SOURCE_DIR="./pdf_extractor_gemini/"
DEST_DIR="./Json_O_Gemini/"

mkdir -p "$DEST_DIR"

echo "Searching for .json files in '$SOURCE_DIR'..."
find "$SOURCE_DIR" -type f -name "*.json" -exec mv -t "$DEST_DIR" {} +

echo "✅ All .json files have been moved to '$DEST_DIR'."
