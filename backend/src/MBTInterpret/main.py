import asyncio
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'MBTInterpret'))
sys.path.append(parent_dir)
from data_extractorAI import process_pdf_file
from constsAI import lines_to_remove, SYSTEM_PROMPT, fixed_text_data, lines_to_remove, page_10_content
from translation import translate_to_hebrew
from utilsAI import get_all_info, get_formatted_type_qualities, format_page_10_content, extract_in_preference_facets, extract_in_preference_facets
from fixed_text import insert_fixed_text
from mbti_to_pdf import generate_mbti_report


async def create_translated_pdf(input_file, output_file):
    # Extract text from the PDF file
    output_dir = r"F:\projects\MBTInfo\output\textfiles"
    save_path = r"F:\projects\MBTInfo\output"
    base_name = os.path.splitext(os.path.basename(input_file))[0][:6]
    extracted_text_path = process_pdf_file(input_file, lines_to_remove)
    try:
        # read the translated text from the Hebrew file
        with open(extracted_text_path, "r", encoding="utf-8") as f:
            cleaned_text = f.read()
            translated_text = await translate_to_hebrew(cleaned_text)
            os.makedirs(output_dir, exist_ok=True)
            translated_file_path = os.path.join(output_dir, f"{base_name}_translated_raw.txt")
            with open(translated_file_path, "w", encoding="utf-8") as translated_file:
                print("translated text saved")
                translated_file.write(translated_text)
            print(f"Translated text saved to {translated_file_path}")
    except Exception as e:
        print("Failed to translate the extracted text to Hebrew.", e)
    mbti_info = get_all_info(translated_file_path)
    mbti_type = mbti_info['type']
    mbti_type_qualities = get_formatted_type_qualities(mbti_type)
    facets = extract_in_preference_facets(translated_file_path)
    formatted_page_10 = format_page_10_content(page_10_content, facets)
    fixed_text_config = fixed_text_data(mbti_info, mbti_type_qualities, formatted_page_10)
    fixes_translated_text_path = os.path.join(output_dir, f"{base_name}_fixed.txt")
    insert_fixed_text(translated_file_path, fixes_translated_text_path, fixed_text_config)
    print(f"Fixed text saved to {fixes_translated_text_path}")
    html_path = os.path.join(output_dir, f"{base_name}_translated.html")
    output_pdf = os.path.join(save_path, f"{base_name}_translated.pdf")
    logo_path = r"F:\projects\MBTInfo\backend\media\full_logo.png"
    first_page_title = "דו&quot;ח בתרגום לעברית עבור: "
    if not os.path.exists(logo_path):
        raise FileNotFoundError(f"Logo file not found at {logo_path}")
    generate_mbti_report(fixes_translated_text_path, html_path, output_pdf, logo_path, first_page_title)
    if not os.path.exists(output_pdf):
        raise FileNotFoundError(f"Final PDF was not generated at {output_pdf}")
    return output_pdf

if __name__ == "__main__":
    input_file = r"F:\projects\MBTInfo\input\ADAM-POMERANTZ-267149-e4b6edb5-1a5f-ef11-bdfd-6045bd04b01a.pdf"
    output_file = r"F:\projects\MBTInfo\output\ADAM-POMERANTZ-267149-e4b6edb5-1a5f-ef11-bdfd-6045bd04b01a_translated.pdf"
    print(asyncio.run(create_translated_pdf(input_file, output_file)))
