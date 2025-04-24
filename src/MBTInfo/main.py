import os
from data_to_excel import process_pdf_to_xl
from data_extractor import extract_and_save_text


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_directory = os.path.dirname(os.path.dirname(current_dir))
    input_directory = os.path.join(root_directory, 'input')
    output_directory = os.path.join(root_directory, 'output')
    os.makedirs(input_directory, exist_ok=True)
    os.makedirs(output_directory, exist_ok=True)
    excel_file = os.path.join(output_directory, 'MBTI_Results.xlsx')
    if os.path.exists(excel_file):
        os.remove(excel_file)
        print(f"Deleted existing {excel_file}")
    for file in os.listdir(input_directory):
        print(file)
        if file.endswith('.pdf'):
            pdf_path = os.path.join(input_directory, file)
            txt_filename = f"{os.path.splitext(file)[0]}_text.txt"
            txt_path = os.path.join(output_directory, txt_filename)
            extract_and_save_text(pdf_path)
            if os.path.exists(txt_path):
                process_pdf_to_xl(txt_path, output_directory)
                print(f'Processed {file}')
            else:
                print(f'Error: Text file not found for {file}')
        else:
            print(f'Skipped {file} (not a PDF file)')

    print(f"All MBTI results have been saved to {excel_file}")


if __name__ == "__main__":
    main()
    print("Processing complete.")
