import os
import openpyxl as xl
from openpyxl.worksheet.table import Table, TableStyleInfo
from utils import get_all_info, find_and_parse_mbti_scores, convert_scores_to_mbti_dict, collect_qualities
from consts import FACETS


def process_pdf_to_xl(text_path, output_dir):
    info = get_all_info(text_path)
    qualities = find_and_parse_mbti_scores(text_path)
    mbti_dict = convert_scores_to_mbti_dict(qualities)
    preferred_qualities, midzone_qualities, out_qualities = collect_qualities(text_path)

    # Convert all qualities to lowercase for case-insensitive comparison
    preferred_qualities = [q.lower() for q in preferred_qualities]
    midzone_qualities = [q.lower() for q in midzone_qualities]
    out_qualities = [q.lower() for q in out_qualities]

    output_filename = 'MBTI_Results.xlsx'
    output_path = os.path.join(output_dir, output_filename)

    headers = ["Name", "Date", "Type", "Extroversion", "Introversion", "Sensing", "Intuition", "Thinking", "Feeling", "Judging", "Perceiving"]
    headers.extend(FACETS)  # Add all facets to the headers

    if os.path.exists(output_path):
        workbook = xl.load_workbook(output_path)
        sheet = workbook.active
    else:
        workbook = xl.Workbook()
        sheet = workbook.active
        sheet.title = 'MBTI Results'
        sheet.append(headers)

    data = [info['name'], info['date'], info['type']] + list(mbti_dict.values())
    
    # Add values for facets
    for header in headers[11:]:  # Start from the 12th column (index 11)
        header_lower = header.lower()
        if header_lower in preferred_qualities:
            data.append('IN-PREF')
        elif header_lower in midzone_qualities:
            data.append('MIDZONE')
        elif header_lower in out_qualities:
            data.append('OUT-OF-PREF')
        else:
            data.append('-')
    
    sheet.append(data)

    # Update the table range to include all columns
    table_range = f"A1:{xl.utils.get_column_letter(len(headers))}{sheet.max_row}"
    if 'Table1' in sheet.tables:
        del sheet.tables['Table1']
    
    tab = Table(displayName="Table1", ref=table_range)
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=True)
    tab.tableStyleInfo = style
    sheet.add_table(tab)

    workbook.save(output_path)
    return output_path


if __name__ == "__main__":
    pdf_path = r"F:\projects\MBTInfo\output\nir-bensinai-MBTI_text.txt"
    output_dir = r"F:\projects\MBTInfo\output"
    output_path = process_pdf_to_xl(pdf_path, output_dir)
    print(f"MBTI results appended to {output_path}")
