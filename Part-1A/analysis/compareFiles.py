import os
import difflib
from pathlib import Path

FOLDER_1 = './Json_O_Gemini/'
FOLDER_2 = './Json_I/'
REPORT_FOLDER = './reports_Gemini/'

def compare_files(file1_path, file2_path):
    with open(file1_path, 'r', encoding='utf-8') as f1:
        content1 = f1.read()
    with open(file2_path, 'r', encoding='utf-8') as f2:
        content2 = f2.read()

    # Calculate similarity ratio
    matcher = difflib.SequenceMatcher(None, content1, content2)
    ratio = matcher.ratio()
    score = round(ratio * 10, 2)  # scale to 1–10

    # Generate diff
    diff = difflib.unified_diff(
        content1.splitlines(keepends=True),
        content2.splitlines(keepends=True),
        fromfile=file1_path,
        tofile=file2_path,
        lineterm=''
    )
    differences = ''.join(diff)

    return score, differences

def generate_report(file_name, score, differences):
    report_path = os.path.join(REPORT_FOLDER, f"{file_name}_report.txt")
    with open(report_path, 'w', encoding='utf-8') as report:
        report.write(f"Similarity Score (1-10): {score}\n")
        report.write("="*50 + "\n")
        report.write("Differences:\n\n")
        if differences:
            report.write(differences)
        else:
            report.write("No differences found. Files are identical.\n")

def main():
    os.makedirs(REPORT_FOLDER, exist_ok=True)

    folder1_files = set(os.listdir(FOLDER_1))
    folder2_files = set(os.listdir(FOLDER_2))

    common_files = folder1_files.intersection(folder2_files)

    if not common_files:
        print("No matching files found across folders.")
        return

    for file_name in common_files:
        path1 = os.path.join(FOLDER_1, file_name)
        path2 = os.path.join(FOLDER_2, file_name)

        print(f"Comparing: {file_name}")
        score, differences = compare_files(path1, path2)
        generate_report(file_name, score, differences)
        print(f"Report generated for {file_name}: {score}/10 similarity")

if __name__ == "__main__":
    main()
