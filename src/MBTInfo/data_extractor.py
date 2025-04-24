import PyPDF2
import os
import glob
import time
import re
from typing import Dict, Union, List


def extract_and_save_text(filepath: str, output_folder: str = None) -> str:
    """
    Extract text from a PDF file, separate by page, and save to a text file in the specified output folder.

    Args:
    filepath (str): The filepath to the PDF file.
    output_folder (str, optional): The folder where the output file will be saved. 
                                   If None, uses the default 'output' folder in the project root.

    Returns:
    str: Path to the saved text file.
    """
    try:
        filename = os.path.basename(filepath)
        
        # Read the PDF file
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            # Extract text from all pages
            all_text = []
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                all_text.append(f"--- Page {page_num} ---\n{page_text}\n")

            # Join all pages with double newline for separation
            text = "\n".join(all_text)

        # Create output filename
        output_filename = f"{os.path.splitext(filename)[0]}_text.txt"
        
        # Determine the output folder path
        if output_folder is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_folder = os.path.join(project_root, 'output')
        
        # Create the output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        output_filepath = os.path.join(output_folder, output_filename)

        # Save text to file
        with open(output_filepath, 'w', encoding='utf-8') as output_file:
            output_file.write(text)

        return output_filepath

    except PyPDF2.errors.PdfReadError as e:
        print(f"Error reading PDF: {e}")
    except IOError as e:
        print(f"I/O error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return ""  # Return empty string if any error occurs

if __name__ == "__main__":
    filepath_test = r"F:\projects\MBTInfo\input\asaf-solomon-267149-4ae2ac9c-005e-ef11-bdfd-6045bd04b01a.pdf"
    result = extract_and_save_text(filepath_test)
    if result:
        print(f"Text saved to: {result}")
    else:
        print("Failed to extract and save text.")
