import os
from data_to_excel import process_pdf_to_xl
from data_extractor import extract_and_save_text
from chart_creator import create_distribution_chart
from formatting_xl import apply_formatting


def process_files(input_directory, output_directory, output_filename):
    os.makedirs(input_directory, exist_ok=True)
    os.makedirs(output_directory, exist_ok=True)
    
    # Create a 'textfiles' subdirectory in the output directory
    textfiles_directory = os.path.join(output_directory, 'textfiles')
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
                process_pdf_to_xl(txt_path, output_directory)
                print(f'Processed {file}')
            else:
                print(f'Error: Text file not found for {file}')
        else:
            print(f'Skipped {file} (not a PDF file)')

    # Apply formatting after processing all files
    apply_formatting(excel_file)
    print(f"Formatting applied to {excel_file}")

    # Create distribution chart
    create_distribution_chart(excel_file)
    print(f"Distribution chart added to {excel_file}")

    print(f"All MBTI results have been saved to {excel_file}")


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_directory = os.path.dirname(os.path.dirname(current_dir))
    input_directory = os.path.join(root_directory, 'input')
    output_directory = os.path.join(root_directory, 'output')
    output_filename = 'MBTI_Results.xlsx'
    process_files(input_directory, output_directory, output_filename)


if __name__ == "__main__":
    main()
    print("Processing complete.")
