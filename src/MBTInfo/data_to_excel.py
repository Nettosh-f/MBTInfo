import os
import csv
import openpyxl as xl
from openpyxl.chart import PieChart, Reference
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import PatternFill, Color
from openpyxl.formatting.rule import ColorScaleRule, Rule
from openpyxl.styles.differential import DifferentialStyle
from utils import get_all_info, find_and_parse_mbti_scores, convert_scores_to_mbti_dict, collect_qualities
from consts import MBTI_TYPES, FACETS, mbti_colors
from collections import Counter
print(FACETS)


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
    print(headers)
    if os.path.exists(output_path):
        workbook = xl.load_workbook(output_path)
        sheet = workbook.active
        # Get the next empty row
        next_row = sheet.max_row + 1
    else:
        workbook = xl.Workbook()
        sheet = workbook.active
        sheet.title = 'MBTI Results'
        sheet.append(headers)
        next_row = 2  # Start data from the second row

    data = [info['name'], info['date'], info['type']] + list(mbti_dict.values())
    
    # Add placeholder values for facets
    data.extend([''] * (len(headers) - len(data)))
    print(preferred_qualities)
    # Loop through headers starting from facets
    for i, header in enumerate(headers[11:], start=11):  # Start from the 12th column (index 11)
        header_lower = header.lower()
        if header_lower in preferred_qualities:
            data[i] = 'IN'
            print(f"Found preferred quality: {header}")
        elif header_lower in midzone_qualities:
            data[i] = 'MID'
            print(f"Found midzone quality: {header}")
        elif header_lower in out_qualities:
            data[i] = 'OUT'
            print(f"Found out-of-preference quality: {header}")
        else:
            data[i] = '-'
            print(f"Quality not found in any list: {header}")
    sheet.append(data)

    # Update the table range to include all new columns
    table_range = f"A1:{xl.utils.get_column_letter(len(headers))}{sheet.max_row}"
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
    sheet = workbook.active
    
    # Define colors
    soft_red = Color(rgb="FFC7CE")  # Light red
    soft_yellow = Color(rgb="FFEB9C")  # Light yellow
    soft_green = Color(rgb="C6EFCE")  # Light green

    for col in range(4, 12):  # 4 to 11 inclusive
        col_letter = xl.utils.get_column_letter(col)
        color_scale_range = f"{col_letter}2:{col_letter}{sheet.max_row}"

        # Rule for black color when value is 0

        # Color scale rule for non-zero values
        color_scale = ColorScaleRule(
            start_type='num', start_value=1, start_color="FFC7CE",  # Soft red for low values
            mid_type='num', mid_value=15, mid_color="FFEB9C",  # Soft yellow for mid values
            end_type='num', end_value=30, end_color="C6EFCE"  # Soft green for high values
        )

        # Apply both rules
        sheet.conditional_formatting.add(color_scale_range, color_scale)

        # Formatting rules for columns L-AZ
    in_fill = PatternFill(start_color="C0CEE6", end_color="C0CEE6", fill_type="solid")
    mid_fill = PatternFill(start_color="D6E1C5", end_color="D6E1C5", fill_type="solid")
    out_fill = PatternFill(start_color="B9CA9D", end_color="B9CA9D", fill_type="solid")

    for col in range(12, 52):  # L to AZ
        col_letter = xl.utils.get_column_letter(col)
        facet_range = f"{col_letter}2:{col_letter}{sheet.max_row}"

        in_rule = Rule(type="cellIs", operator="equal", formula=['"IN"'],
                       stopIfTrue=False, dxf=DifferentialStyle(fill=in_fill))
        mid_rule = Rule(type="cellIs", operator="equal", formula=['"MID"'],
                        stopIfTrue=False, dxf=DifferentialStyle(fill=mid_fill))
        out_rule = Rule(type="cellIs", operator="equal", formula=['"OUT"'],
                        stopIfTrue=False, dxf=DifferentialStyle(fill=out_fill))

        sheet.conditional_formatting.add(facet_range, in_rule)
        sheet.conditional_formatting.add(facet_range, mid_rule)
        sheet.conditional_formatting.add(facet_range, out_rule)

    # Apply conditional formatting for MBTI types in column C
    for mbti_type, color in mbti_colors.items():
        mbti_rule = Rule(
            type="cellIs",
            operator="equal",
            formula=[f'"{mbti_type}"'],
            stopIfTrue=False,
            dxf=DifferentialStyle(fill=PatternFill(start_color=color, end_color=color, fill_type="solid"))
        )
        sheet.conditional_formatting.add(f"C2:C{sheet.max_row}", mbti_rule)

    workbook.save(output_path)
    return output_path


if __name__ == "__main__":
    pdf_path = r"F:\projects\MBTInfo\output\nir-bensinai-MBTI_text.txt"
    output_dir = r"F:\projects\MBTInfo\output"
    output_path = process_pdf_to_xl(pdf_path, output_dir)
    print(f"MBTI results appended to {output_path}")
