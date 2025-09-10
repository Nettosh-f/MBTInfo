# File: group_report.py - Fixed version
import os
import openpyxl as xl
from data_to_excel import process_pdf_to_xl
from data_extractor import extract_and_save_text
from chart_creator import create_distribution_charts
from formatting import format_xl
from create_section_sheets import create_section_sheets
from create_facet_table import create_facet_table
from utils import reorder_sheets


def process_group_report_fixed(input_directory, output_directory, output_filename):
    """Fixed version of process_group_report with better error handling and file path management"""

    print(f"\n🚀 Starting group report processing...")
    print(f"📁 Input: {input_directory}")
    print(f"📁 Output: {output_directory}")
    print(f"📄 File: {output_filename}")

    # Create directories
    textfiles_directory = os.path.join(output_directory, 'textfiles')
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(textfiles_directory, exist_ok=True)

    excel_file = os.path.join(output_directory, output_filename)
    if os.path.exists(excel_file):
        os.remove(excel_file)
        print(f"🗑️ Deleted existing {excel_file}")

    # Track processing
    processed_files = 0
    failed_files = []

    # Get list of PDF files
    pdf_files = [f for f in os.listdir(input_directory) if f.lower().endswith('.pdf')]
    print(f"📄 Found {len(pdf_files)} PDF files")

    if not pdf_files:
        print("❌ No PDF files found!")
        return False

    # Process each PDF file
    for file in pdf_files:
        print(f"\n📄 Processing: {file}")
        pdf_path = os.path.join(input_directory, file)

        # Check file size
        file_size = os.path.getsize(pdf_path)
        print(f"📊 File size: {file_size} bytes")

        if file_size == 0:
            print(f"⚠️ Skipping empty file: {file}")
            failed_files.append(f"{file} - Empty file")
            continue

        try:
            # Extract text with improved method
            txt_path = extract_and_save_text(pdf_path, textfiles_directory)
            print(f"🔍 Text extraction result: {txt_path}")

            # Check if extraction was successful
            if not txt_path:
                print(f'❌ Text extraction returned None for {file}')
                failed_files.append(f"{file} - Text extraction returned None")
                continue

            # Handle both absolute path and just filename returns from extract_and_save_text
            if os.path.isabs(txt_path):
                # If it's an absolute path, use it directly
                actual_txt_path = txt_path
            else:
                # If it's just a filename, construct the full path
                actual_txt_path = os.path.join(textfiles_directory, txt_path)

            print(f"📝 Looking for text file at: {actual_txt_path}")

            if os.path.exists(actual_txt_path):
                # Check if text file has content
                txt_size = os.path.getsize(actual_txt_path)
                print(f"📝 Text file size: {txt_size} bytes")

                if txt_size > 50:  # Require minimum content (more than just headers)
                    # Process to Excel - use the actual path
                    process_pdf_to_xl(actual_txt_path, output_directory, 'MBTI Results', output_filename)
                    processed_files += 1
                    print(f'✅ Successfully processed {file}')
                else:
                    print(f'⚠️ Text file too small ({txt_size} bytes) for {file}')
                    failed_files.append(f"{file} - Text file too small ({txt_size} bytes)")
            else:
                # Debug: List what files actually exist in textfiles directory
                existing_files = os.listdir(textfiles_directory) if os.path.exists(textfiles_directory) else []
                print(f'❌ Text file not found: {actual_txt_path}')
                print(f'🔍 Files in textfiles directory: {existing_files}')

                # Try to find a similar file (in case of naming issues)
                base_name = os.path.splitext(file)[0]  # Remove .pdf extension
                possible_matches = [f for f in existing_files if
                                    base_name in f or any(part in f for part in base_name.split('_'))]

                if possible_matches:
                    print(f'🔍 Possible matches found: {possible_matches}')
                    # Try using the first match
                    match_path = os.path.join(textfiles_directory, possible_matches[0])
                    if os.path.exists(match_path) and os.path.getsize(match_path) > 50:
                        print(f'✅ Using matched file: {possible_matches[0]}')
                        process_pdf_to_xl(match_path, output_directory, 'MBTI Results', output_filename)
                        processed_files += 1
                        print(f'✅ Successfully processed {file} (using matched text file)')
                        continue

                failed_files.append(f"{file} - Text file not found at {actual_txt_path}")

        except Exception as e:
            print(f'❌ Error processing {file}: {e}')
            import traceback
            traceback.print_exc()
            failed_files.append(f"{file} - {str(e)}")

    # Print summary
    print(f"\n📊 PROCESSING SUMMARY:")
    print(f"✅ Successfully processed: {processed_files} files")
    print(f"❌ Failed: {len(failed_files)} files")

    if failed_files:
        print(f"\n❌ FAILED FILES:")
        for failure in failed_files:
            print(f"  - {failure}")

    # Only proceed with workbook operations if we processed files
    if processed_files > 0 and os.path.exists(excel_file):
        try:
            print(f"\n📊 Creating charts and additional sheets...")

            workbook = xl.load_workbook(excel_file)

            print("🔄 Creating distribution charts...")
            create_distribution_charts(workbook)

            print("🔄 Creating section sheets...")
            create_section_sheets(textfiles_directory, workbook)

            print("🔄 Creating facet table...")
            create_facet_table(workbook)

            print("💾 Saving workbook...")
            workbook.save(excel_file)

            print("🎨 Formatting Excel file...")
            format_xl(excel_file)

            print("📑 Reordering sheets...")
            reorder_sheets(excel_file)

            print(f"✅ Group report completed: {excel_file}")
            return workbook

        except Exception as e:
            print(f"❌ Error finalizing workbook: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print(f"❌ No valid files were processed successfully")
        if not os.path.exists(excel_file):
            print(f"❌ Excel file was not created: {excel_file}")
        return False


# Alternative debug function to check what extract_and_save_text is actually returning
def debug_text_extraction(pdf_path, textfiles_directory):
    """Debug function to understand what extract_and_save_text returns"""
    print(f"\n🔍 DEBUG: Testing text extraction for {pdf_path}")
    print(f"🔍 Target directory: {textfiles_directory}")

    try:
        result = extract_and_save_text(pdf_path, textfiles_directory)
        print(f"🔍 extract_and_save_text returned: {result}")
        print(f"🔍 Type of result: {type(result)}")

        if result:
            # Check different path constructions
            if os.path.isabs(result):
                print(f"🔍 Result is absolute path: {result}")
                print(f"🔍 File exists: {os.path.exists(result)}")
            else:
                constructed_path = os.path.join(textfiles_directory, result)
                print(f"🔍 Constructed path: {constructed_path}")
                print(f"🔍 File exists: {os.path.exists(constructed_path)}")

        # List all files in the target directory
        if os.path.exists(textfiles_directory):
            files = os.listdir(textfiles_directory)
            print(f"🔍 Files in directory: {files}")
        else:
            print(f"🔍 Directory doesn't exist: {textfiles_directory}")

    except Exception as e:
        print(f"🔍 Exception during extraction: {e}")
        import traceback
        traceback.print_exc()


def main():
    input_directory = r"C:\Users\user\Downloads\שאלונים של זמינגו\שאלונים של זמינגו"
    output_directory = r"F:\projects\MBTInfo\output"
    output_filename = "MBTI_Results_Zamingo.xlsx"

    process_group_report_fixed(input_directory, output_directory, output_filename)
    print("Group report processing complete.")


if __name__ == "__main__":
    main()