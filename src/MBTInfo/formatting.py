import openpyxl as xl
from openpyxl.styles import PatternFill, Color, Font
from openpyxl.formatting.rule import ColorScaleRule, Rule, FormulaRule
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.utils import get_column_letter
from consts import mbti_colors


def adjust_column_widths(sheet):
    for col in range(1, sheet.max_column + 1):
        max_length = 0
        column_letter = get_column_letter(col)
        for row in range(1, sheet.max_row + 1):
            cell = sheet.cell(row=row, column=col)
            if isinstance(cell, xl.cell.cell.MergedCell):
                continue
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        sheet.column_dimensions[column_letter].width = adjusted_width


def format_xl(file_path):
    workbook = xl.load_workbook(file_path)
    sheet = workbook.active
    adjust_column_widths(sheet)
    # colors:
    black_fill = PatternFill(start_color='FF000000', end_color='FF000000', fill_type='solid')
    light_green = 'ffb7e5b7'
    light_yellow = 'ffe5e589'
    light_red = 'ffe5b7b7'

    # handling MBTI type colors
    mbti_range = f"C2:C{sheet.max_row}"
    for mbti_type, color in mbti_colors.items():
        mbti_rule = Rule(
            type="cellIs",
            operator="equal",
            formula=[f'"{mbti_type}"'],
            stopIfTrue=False,
            dxf=DifferentialStyle(fill=PatternFill(start_color=color, end_color=color, fill_type="solid"))
        )
        sheet.conditional_formatting.add(mbti_range, mbti_rule)
    # handling qualities scores
    scores_range = f"D2:K{sheet.max_row}"
    formula = 'OR(D2<1,D2>30)'
    zero_rule = FormulaRule(formula=[formula], stopIfTrue=True, fill=black_fill)
    sheet.conditional_formatting.add(scores_range, zero_rule)
    color_scale_rule = ColorScaleRule(
        start_type='num',start_value=1, start_color=light_green,
        mid_type='num', mid_value=15, mid_color=light_yellow,
        end_type='num', end_value=30, end_color=light_red,
    )
    sheet.conditional_formatting.add(scores_range, color_scale_rule)
    # handling in-preference formatting
    inpref_fill = PatternFill(start_color='FFC0CEE6', end_color='FFC0CEE6', fill_type='solid')
    midzone_fill = PatternFill(start_color='FFD6E1C5', end_color='FFD6E1C5', fill_type='solid')
    outofpref_fill = PatternFill(start_color='FFB9CA9D', end_color='FFB9CA9D', fill_type='solid')
    dash_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
    facets_range = f"L2:AY{sheet.max_row}"
    inpref_rule = FormulaRule(formula=['L2="IN-PREF"'], fill=inpref_fill)
    midzone_rule = FormulaRule(formula=['L2="MIDZONE"'], fill=midzone_fill)
    outofpref_rule = FormulaRule(formula=['L2="OUT-OF-PREF"'], fill=outofpref_fill)
    dash_rule = FormulaRule(formula=['L2="-"'], fill=dash_fill)
    sheet.conditional_formatting.add(facets_range, inpref_rule)
    sheet.conditional_formatting.add(facets_range, midzone_rule)
    sheet.conditional_formatting.add(facets_range, outofpref_rule)
    sheet.conditional_formatting.add(facets_range, dash_rule)
    workbook.save(file_path)
    print(f"Formatting applied to {file_path} successfully.")


if __name__ == "__main__":
    # For testing purposes
    format_xl(r"F:\projects\MBTInfo\output\MBTI_Results.xlsx")