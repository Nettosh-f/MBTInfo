import openpyxl
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Font, PatternFill
from formatting import adjust_column_widths
from collections import Counter


def create_facet_table(workbook):
    sheet_name = "Facet Table"
    
    # Check if the sheet already exists
    if sheet_name in workbook.sheetnames:
        # Remove the existing sheet
        workbook.remove(workbook[sheet_name])
    
    # Create a new sheet
    sheet = workbook.create_sheet(title=sheet_name)

    # Define headers
    headers = [
        "Name", "Date", "Type",
        "Appearing 3 times(1)", "Appearing 3 times(2)", "Appearing 3 times(3)",
        "Appearing 2 times(1)", "Appearing 2 times(2)", "Appearing 2 times(3)", "Appearing 2 times(4)", "Appearing 2 times(5)",
        "Appearing 1 time(1)", "Appearing 1 time(2)", "Appearing 1 time(3)", "Appearing 1 time(4)",
        "Appearing 1 time(5)", "Appearing 1 time(6)", "Appearing 1 time(7)", "Appearing 1 time(8)", "Appearing 1 time(9)"
    ]

    # Define column colors
    three_times_color = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # Light green
    two_times_color = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")    # Light yellow
    one_time_color = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")     # Light red

    # Write headers
    for col, header in enumerate(headers, start=1):
        cell = sheet.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        
        # Apply colors to header cells based on column groups
        if 4 <= col <= 6:  # Columns D, E, F (3 times)
            cell.fill = three_times_color
        elif 7 <= col <= 11:  # Columns G, H, I, J, K (2 times)
            cell.fill = two_times_color
        elif 12 <= col <= 20:  # Columns L through T (1 time)
            cell.fill = one_time_color

    # Get the 'MBTI Results' sheet
    mbti_results_sheet = workbook['MBTI Results']
    max_row = mbti_results_sheet.max_row

    # Process each row
    for row in range(2, max_row + 1):
        target_row = row  # Start from row 2 in the Facet Table

        # Copy Name, Date, and Type
        for col in range(1, 4):
            sheet.cell(row=target_row, column=col, value=mbti_results_sheet.cell(row=row, column=col).value)

        # Get facets from AZ to BZ
        facets = [cell.value for cell in mbti_results_sheet[row][51:78] if cell.value]  # AZ is column 52

        # Count facet occurrences
        facet_counts = Counter(facets)

        # Write facets in order: 3 timers, 2 timers, 1 timers
        col = 4
        for count in [3, 2, 1]:
            facets_with_count = [facet for facet, c in facet_counts.items() if c == count]
            for facet in facets_with_count:
                sheet.cell(row=target_row, column=col, value=facet)
                col += 1
            
            # Move to the next group of columns
            if count == 3:
                col = 7  # Move to "Appearing 2 times" columns
            elif count == 2:
                col = 12  # Move to "Appearing 1 time" columns

    # Check column F and move content from E to F if F is empty
    for row in range(2, sheet.max_row + 1):
        if sheet.cell(row=row, column=6).value is None:  # Column F is empty
            e_value = sheet.cell(row=row, column=5).value
            if e_value:
                sheet.cell(row=row, column=6, value=e_value)
                sheet.cell(row=row, column=5, value="")  # Clear cell E

    # Check column K and move content from J to K if K is empty
    for row in range(2, sheet.max_row + 1):
        if sheet.cell(row=row, column=11).value is None:  # Column K is empty
            j_value = sheet.cell(row=row, column=10).value
            i_value = sheet.cell(row=row, column=9).value
            h_value = sheet.cell(row=row, column=8).value
            if j_value:
                sheet.cell(row=row, column=11, value=j_value)
                sheet.cell(row=row, column=10, value=i_value)
                sheet.cell(row=row, column=9, value=h_value)
                sheet.cell(row=row, column=8, value="")

    # Create table
    table_ref = f"A1:T{max_row}"
    table = Table(displayName="FacetTable", ref=table_ref)
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    table.tableStyleInfo = style
    sheet.add_table(table)

    # Adjust column widths
    adjust_column_widths(sheet)

    return workbook


if __name__ == "__main__":
    # For testing purposes
    workbook_path = r"F:\projects\MBTInfo\output\MBTI_Results.xlsx"
    workbook = openpyxl.load_workbook(workbook_path)
    create_facet_table(workbook)
    workbook.save(workbook_path)