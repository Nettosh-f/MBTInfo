import PyPDF2
import os
import glob
import time
import re
from typing import Dict, Union, List


def extract_and_save_text(filepath: str, output_folder: str) -> str:
    try:
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

        filename = os.path.basename(filepath)
        output_filename = f"{os.path.splitext(filename)[0]}_text.txt"
        output_path = os.path.join(output_folder, output_filename)

        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(text)

        return output_path
    except Exception as e:
        print(f"Error processing {filepath}: {str(e)}")
        return ""  # Return empty string if any error occurs


if __name__ == "__main__":
    filepath_test = r"F:\projects\MBTInfo\input\asaf-solomon-267149-4ae2ac9c-005e-ef11-bdfd-6045bd04b01a.pdf"
    output_folder = r"F:\projects\MBTInfo\output\textfiles"
    result = extract_and_save_text(filepath_test, output_folder)
    if result:
        print(f"Text saved to: {result}")
    else:
        print("Failed to extract and save text.")
