import os
import csv
import openpyxl as xl
from openpyxl.worksheet.table import Table, TableStyleInfo
from utils import get_all_info, find_and_parse_mbti_scores, convert_scores_to_mbti_dict
from consts import MBTI_TYPES


def process_pdf_to_xl(text_path, output_dir):
    info = get_all_info(text_path)
    qualities = find_and_parse_mbti_scores(text_path)
    mbti_dict = convert_scores_to_mbti_dict(qualities)
    output_filename = 'MBTI_Results.xlsx'
    output_path = os.path.join(output_dir, output_filename)
    if os.path.exists(output_path):
        workbook = xl.load_workbook(output_path)
        sheet = workbook.active
        # Get the next empty row
        next_row = sheet.max_row + 1
    else:
        workbook = xl.Workbook()
        sheet = workbook.active
        sheet.title = 'MBTI Results'
        headers = ["Name", "Date", "Type", "Extroversion", "Introversion", "Sensing", "Intuition", "Thinking", "Feeling", "Judging", "Perceiving"]
        sheet.append(headers)
        next_row = 2  # Start data from the second row
    data = [info['name'], info['date'], info['type']] + list(mbti_dict.values())
    sheet.append(data)
    table_range = f"A1:K{sheet.max_row}"
    if 'Table1' in sheet.tables:
        del sheet.tables['Table1']
    
    tab = Table(displayName="Table1", ref=table_range)
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=True)
    tab.tableStyleInfo = style

    sheet.add_table(tab)
    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        sheet.column_dimensions[column_letter].width = adjusted_width
    workbook.save(output_path)
    return output_path


if __name__ == "__main__":
    pdf_path = r"F:\projects\MBTInfo\output\nir-bensinai-MBTI_text.txt"
    output_dir = r"F:\projects\MBTInfo\output"
    output_path = process_pdf_to_xl(pdf_path, output_dir)
    print(f"MBTI results appended to {output_path}")
