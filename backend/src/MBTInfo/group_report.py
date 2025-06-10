# File: F:\projects\MBTInfo\backend\src\MBTInfo\group_report.py
import os
import openpyxl as xl
from data_to_excel import process_pdf_to_xl
from data_extractor import extract_and_save_text
from chart_creator import create_distribution_charts
from formatting import format_xl
from create_section_sheets import create_section_sheets
from create_facet_table import create_facet_table
from utils import reorder_sheets


def process_group_report(input_directory, output_directory, output_filename):
    textfiles_directory = os.path.join(output_directory, 'textfiles')
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(textfiles_directory, exist_ok=True)

    excel_file = os.path.join(output_directory, output_filename)
    if os.path.exists(excel_file):
        os.remove(excel_file)
        print(f"Deleted existing {excel_file}")

    for file in os.listdir(input_directory):
        if file.endswith('.pdf'):
            pdf_path = os.path.join(input_directory, file)
            txt_filename = f"{os.path.splitext(file)[0]}_text.txt"
            txt_path = os.path.join(textfiles_directory, txt_filename)
            extract_and_save_text(pdf_path, textfiles_directory)
            if os.path.exists(txt_path):
                process_pdf_to_xl(txt_path, output_directory, 'MBTI Results', output_filename)
                print(f'Processed {file}')
            else:
                print(f'Error: Text file not found for {file}')
        else:
            print(f'Skipped {file} (not a PDF file)')

    workbook = xl.load_workbook(excel_file)
    create_distribution_charts(workbook)
    create_section_sheets(textfiles_directory, workbook)
    create_facet_table(workbook)
    workbook.save(excel_file)
    format_xl(excel_file)
    reorder_sheets(excel_file)
    print(f"All MBTI results, charts, and section sheets have been saved to {excel_file}")



def main():
    input_directory = r"F:\projects\MBTInfo\input\דוחות של כל אלעל\דוחות של כל אלעל"
    output_directory = r"F:\projects\MBTInfo\output"
    output_filename = "MBTI_Results_EL_AL.xlsx"

    process_group_report(input_directory, output_directory, output_filename)
    print("Group report processing complete.")


if __name__ == "__main__":
    main()