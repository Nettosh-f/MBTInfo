import os
from data_to_excel import process_pdf_to_xl
from data_extractor import extract_and_save_text
from chart_creator import create_distribution_charts
from formatting import format_xl
from create_section_sheets import create_section_sheets
from create_facet_table import create_facet_table  # Add this import
import openpyxl as xl


def process_files(input_directory, output_directory, output_filename, textfiles_directory):
    os.makedirs(input_directory, exist_ok=True)
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(textfiles_directory, exist_ok=True)

    excel_file = os.path.join(output_directory, output_filename)
    if os.path.exists(excel_file):
        os.remove(excel_file)
        print(f"Deleted existing {excel_file}")

    for file in os.listdir(input_directory):
        print(file)
        if file.endswith('.pdf'):
            pdf_path = os.path.join(input_directory, file)
            txt_filename = f"{os.path.splitext(file)[0]}_text.txt"
            txt_path = os.path.join(textfiles_directory, txt_filename)
            extract_and_save_text(pdf_path, textfiles_directory)
            if os.path.exists(txt_path):
                # Add 'MBTI Results' as the sheet name
                process_pdf_to_xl(txt_path, output_directory, 'MBTI Results', output_filename)
                print(f'Processed {file}')
            else:
                print(f'Error: Text file not found for {file}')
        else:
            print(f'Skipped {file} (not a PDF file)')

    # Load the workbook
    workbook = xl.load_workbook(excel_file)

    # Create distribution charts
    create_distribution_charts(workbook)
    print("Distribution charts added to workbook")

    # Add section sheets to the main workbook
    create_section_sheets(textfiles_directory, workbook)
    print("Section sheets added to workbook")

    # Create a facet table
    create_facet_table(workbook)  # Remove the assignment
    print("Facet table added to workbook")


    # Create charts (this seems redundant, as we already created distribution charts)
    # create_distribution_charts(workbook)  # Comment this out or remove it

    # Save the workbook with all changes
    workbook.save(excel_file)
    print(f"All MBTI results, charts, and section sheets have been saved to {excel_file}")
    # Apply formatting after processing all files
    format_xl(excel_file)
    print(f"Formatting applied to {excel_file}")
    return workbook  # Return the workbook object


def main():
    input_directory = r"F:\projects\MBTInfo\input"
    output_directory = r"F:\projects\MBTInfo\output"
    result_sheet_name = "MBTI Results"
    output_filename = "MBTI_Results.xlsx"
    output_path = os.path.join(output_directory, output_filename)

    # Process PDFs and create Excel file
    for filename in os.listdir(input_directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_directory, filename)
            text_path = extract_and_save_text(pdf_path, output_directory)
            if text_path:
                process_pdf_to_xl(text_path, output_directory, result_sheet_name, output_filename)

    # Load the workbook
    workbook = xl.load_workbook(output_path)

    # Create section sheets
    workbook = create_section_sheets(output_directory, workbook)

    # Create facet table
    workbook = create_facet_table(workbook)  # Add this line

    # Create charts
    workbook = create_distribution_charts(workbook)

    # Save the workbook
    workbook.save(output_path)

    # Apply formatting
    format_xl(output_path)

    print(f"Processing complete. Results saved to {output_path}")


def create_pie_chart(chart_sheet, data_range, title):
    pie = PieChart()
    sheet_name = chart_sheet.title
    labels = Reference(chart_sheet, range_string=f"{sheet_name}!{data_range.split(':')[0]}")
    data = Reference(chart_sheet, range_string=f"{sheet_name}!{data_range}")
    pie.add_data(data, titles_from_data=True)
    pie.set_categories(labels)
    pie.title = title
    
    # Add data labels
    pie.dataLabels = openpyxl.chart.label.DataLabelList()
    pie.dataLabels.showCatName = True
    pie.dataLabels.showVal = True
    pie.dataLabels.showPercent = True
    
    return pie

def create_facet_chart(workbook, chart_sheet):
    # ... (previous code remains the same)

    # Create stacked bar chart
    chart = BarChart()
    chart.type = "bar"
    chart.stacked = True
    chart.title = "Facet Distribution"
    chart.y_axis.title = "Facets"
    chart.x_axis.title = "Count"
    
    sheet_name = chart_sheet.title
    # Add data to chart
    data = Reference(chart_sheet, min_col=2, min_row=start_row, max_row=start_row+20, max_col=4)
    cats = Reference(chart_sheet, min_col=1, min_row=start_row+1, max_row=start_row+20)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)

    # ... (rest of the function remains the same)

if __name__ == "__main__":
    main()
    print("Processing complete.")
