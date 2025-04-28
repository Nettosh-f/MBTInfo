import openpyxl
from openpyxl.chart import PieChart, Reference
from openpyxl.chart.series import DataPoint
from openpyxl.styles import Font, PatternFill
from collections import Counter
from consts import mbti_colors


def create_distribution_chart(workbook):
    # Get the 'MBTI Results' sheet
    if 'MBTI Results' in workbook.sheetnames:
        main_sheet = workbook['MBTI Results']
    else:
        main_sheet = workbook.active  # Fallback to the active sheet if 'MBTI Results' doesn't exist
    
    # Count MBTI types
    mbti_counts = Counter(cell.value for cell in main_sheet['C'][1:] if cell.value)
    
    # Create a new sheet for the chart
    chart_sheet = workbook.create_sheet(title="MBTI Distribution")
    
    # Write data to the new sheet
    chart_sheet['A1'] = "MBTI Type"
    chart_sheet['B1'] = "Count"
    chart_sheet['A1'].font = Font(bold=True)
    chart_sheet['B1'].font = Font(bold=True)
    
    for row, (mbti_type, count) in enumerate(mbti_counts.items(), start=2):
        chart_sheet[f'A{row}'] = mbti_type
        chart_sheet[f'B{row}'] = count
        if mbti_type in mbti_colors:
            chart_sheet[f'A{row}'].fill = PatternFill(start_color=mbti_colors[mbti_type],
                                                     end_color=mbti_colors[mbti_type],
                                                      fill_type="solid")
    # Create pie chart
    pie = PieChart()
    labels = Reference(chart_sheet, min_col=1, min_row=2, max_row=len(mbti_counts)+1)
    data = Reference(chart_sheet, min_col=2, min_row=1, max_row=len(mbti_counts)+1)
    pie.add_data(data, titles_from_data=True)
    pie.set_categories(labels)
    pie.title = "Distribution by Type"
    
    # Add data labels
    pie.dataLabels = openpyxl.chart.label.DataLabelList()
    pie.dataLabels.showCatName = True
    pie.dataLabels.showVal = True
    pie.dataLabels.showPercent = True
    
    # Set colors for each slice of the pie chart
    for i, (mbti_type, _) in enumerate(mbti_counts.items()):
        if mbti_type in mbti_colors:
            slice = DataPoint(idx=i)
            slice.graphicalProperties.solidFill = mbti_colors[mbti_type]
            pie.series[0].dPt.append(slice)
    
    # Add the chart to the sheet
    chart_sheet.add_chart(pie, "D2")
    
    # Adjust column widths
    for column in chart_sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        chart_sheet.column_dimensions[column_letter].width = adjusted_width
    
    # No need to save the workbook here, as it will be saved in the main function

if __name__ == "__main__":
    # For testing purposes
    import openpyxl
    workbook_path = r"F:\projects\MBTInfo\output\MBTI_Results.xlsx"
    workbook = openpyxl.load_workbook(workbook_path)
    create_distribution_chart(workbook)
    workbook.save(workbook_path)